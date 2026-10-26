from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, RateLimitError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from decision_mirror.extraction.llm_client import GroqClient, LLMClient
from decision_mirror.extraction.pipeline import run_item
from decision_mirror.extraction.prompt_loader import load_prompt
from decision_mirror.extraction.validation import classify_response

EVAL_PATH = ROOT / "data" / "processed" / "eval_set_v1.json"
RUNS_DIR = ROOT / "evaluation" / "runs"
RESPONSE_FORMAT = {"type": "json_object"}
MAX_BATCH_SIZE = 10


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _model_slug(model: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", model).strip("-._")
    if not slug:
        raise ValueError("model name cannot produce an empty run-id slug")
    return slug


def _read_jsonl(path: Path, *, repair_partial_tail: bool = False) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        last_newline = data.rfind(b"\n")
        if repair_partial_tail:
            with path.open("r+b") as stream:
                stream.truncate(last_newline + 1 if last_newline >= 0 else 0)
                stream.flush()
                os.fsync(stream.fileno())
        data = data[: last_newline + 1] if last_newline >= 0 else b""

    rows = []
    for line_number, line in enumerate(data.splitlines(), 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"Invalid JSONL in {path} at line {line_number}"
            ) from error
        if not isinstance(value, dict):
            raise RuntimeError(f"Expected JSON object in {path} at line {line_number}")
        rows.append(value)
    return rows


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    encoded = _json_bytes(record) + b"\n"
    with path.open("ab") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _select_items(
    items: list[dict[str, Any]], gold_set: str, split: str
) -> list[dict[str, Any]]:
    return [
        item
        for item in items
        if (gold_set == "all" or item["gold_set"] == gold_set)
        and (split == "all" or item["split"] == split)
    ]


def _retry_after_seconds(error: RateLimitError) -> float | None:
    value = error.response.headers.get("retry-after")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(
                0.0,
                (retry_at - datetime.now(timezone.utc)).total_seconds(),
            )
        except (TypeError, ValueError, OverflowError):
            return None


def _api_error_status(error: Exception) -> int | None:
    return error.status_code if isinstance(error, APIStatusError) else None


def _is_transient(error: Exception) -> bool:
    return (
        isinstance(error, (RateLimitError, APIConnectionError, TimeoutError))
        or (
            isinstance(error, APIStatusError)
            and (error.status_code == 408 or error.status_code >= 500)
        )
    )


def _new_run_path(base_id: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    candidate = RUNS_DIR / f"{base_id}__{timestamp}"
    suffix = 1
    while candidate.exists():
        candidate = RUNS_DIR / f"{base_id}__{timestamp}-{suffix}"
        suffix += 1
    return candidate


def _make_manifest(
    *,
    run_id: str,
    prompt_version: str,
    prompt_sha256: str,
    model: str,
    temperature: float,
    max_completion_tokens: int,
    reasoning_effort: str,
    eval_set_sha256: str,
    split: str,
    batch_size: int,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "prompt_version": prompt_version,
        "prompt_sha256": prompt_sha256,
        "model": model,
        "temperature": temperature,
        "max_completion_tokens": max_completion_tokens,
        "reasoning_effort": reasoning_effort,
        "response_format": RESPONSE_FORMAT,
        "eval_set_sha256": eval_set_sha256,
        "split": split,
        "created_at": _utc_now(),
        "batch_size": batch_size,
    }


def _check_manifest(
    existing: dict[str, Any], requested: dict[str, Any]
) -> None:
    fields = (
        "prompt_version",
        "prompt_sha256",
        "model",
        "temperature",
        "max_completion_tokens",
        "reasoning_effort",
        "response_format",
        "eval_set_sha256",
        "split",
        "batch_size",
    )
    changed = [field for field in fields if existing.get(field) != requested[field]]
    if changed:
        raise RuntimeError(
            "Run manifest mismatch for "
            + ", ".join(changed)
            + "; use --new-run or change nothing."
        )


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _status() -> None:
    items = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_dirs = sorted(path for path in RUNS_DIR.iterdir() if path.is_dir())
    if not run_dirs:
        print("No extraction runs found.")
        return
    for run_dir in run_dirs:
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.exists():
            print(f"{run_dir.name}: missing manifest")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        selected = _select_items(items, manifest.get("set", "all"), manifest["split"])
        responses = _read_jsonl(run_dir / "raw_responses.jsonl")
        attempts = _read_jsonl(run_dir / "attempts.log.jsonl")
        final_ids = {row["item_id"] for row in responses}
        failed_ids = {
            row["item_id"] for row in attempts if row["item_id"] not in final_ids
        }
        print(
            f"{run_dir.name}: {len(final_ids)}/{len(selected)} final | "
            f"{len(failed_ids)} pending retry"
        )


def run_invocation(
    *,
    prompt_version: str,
    gold_set: str,
    split: str,
    batch_size: int = 10,
    model: str | None = None,
    client: LLMClient | None = None,
    status: bool = False,
    dry_run: bool = False,
    retry_api_failures: bool = False,
    new_run: bool = False,
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    if status:
        _status()
        return 0
    if not 1 <= batch_size <= MAX_BATCH_SIZE:
        raise ValueError(f"--batch-size must be between 1 and {MAX_BATCH_SIZE}")

    load_dotenv()
    try:
        prompt, prompt_sha256 = load_prompt(prompt_version)
    except ValueError as error:
        if "legacy" in str(error).casefold():
            raise ValueError(f"Refusing to run a legacy prompt: {error}") from error
        raise

    temperature = float(os.getenv("GROQ_TEMPERATURE", "0"))
    max_completion_tokens = int(os.getenv("GROQ_MAX_TOKENS", "4096"))
    reasoning_effort = os.getenv("GROQ_REASONING_EFFORT", "medium")
    model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    request_delay = float(os.getenv("REQUEST_DELAY_SECONDS", "3"))
    eval_bytes = EVAL_PATH.read_bytes()
    eval_set_sha256 = _sha256(eval_bytes)
    items = json.loads(eval_bytes)
    selected = _select_items(items, gold_set, split)
    if not selected:
        print(f"No evaluation items selected for {gold_set}-{split}; RUN COMPLETE")
        return 0

    run_id = (
        f"{prompt_version}__{_model_slug(model)}__{gold_set}-{split}__"
        f"{eval_set_sha256[:8]}"
    )
    manifest = _make_manifest(
        run_id=run_id,
        prompt_version=prompt_version,
        prompt_sha256=prompt_sha256,
        model=model,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        reasoning_effort=reasoning_effort,
        eval_set_sha256=eval_set_sha256,
        split=split,
        batch_size=batch_size,
    )
    manifest["set"] = gold_set

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = _new_run_path(run_id) if new_run else RUNS_DIR / run_id
    manifest["run_directory"] = run_dir.name
    manifest_path = run_dir / "manifest.json"
    responses_path = run_dir / "raw_responses.jsonl"
    attempts_path = run_dir / "attempts.log.jsonl"
    if run_dir.exists():
        if new_run:
            raise RuntimeError("Could not create a unique --new-run directory.")
        if not manifest_path.exists():
            raise RuntimeError(
                f"Existing run directory has no manifest: {run_dir}; "
                "use --new-run or change nothing."
            )
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        _check_manifest(existing, manifest)
    if run_dir.exists():
        final_rows = _read_jsonl(responses_path, repair_partial_tail=not dry_run)
    else:
        final_rows = []
    final_ids = {row["item_id"] for row in final_rows}
    if len(final_ids) != len(final_rows):
        raise RuntimeError(f"Duplicate final item records found in {responses_path}")
    pending = [item for item in selected if item["item_id"] not in final_ids]
    batch = pending[:batch_size]
    if dry_run:
        print(f"Run {run_dir.name}: dry run; next items ({len(batch)}):")
        for item in batch:
            print(f"  {item['item_id']}")
        return 0

    if client is None:
        client = GroqClient(
            model=model,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            reasoning_effort=reasoning_effort,
            response_format=RESPONSE_FORMAT,
        )

    if not run_dir.exists():
        run_dir.mkdir(parents=True)
        _write_manifest(manifest_path, manifest)
        responses_path.touch()
        attempts_path.touch()

    attempt_history = _read_jsonl(attempts_path, repair_partial_tail=True)
    prior_attempt_counts: dict[str, int] = {}
    for row in attempt_history:
        item_id = row["item_id"]
        prior_attempt_counts[item_id] = prior_attempt_counts.get(item_id, 0) + 1
    current_final: list[dict[str, Any]] = []
    quota_reached = False

    for item_index, item in enumerate(batch):
        attempts = 0
        while True:
            attempts += 1
            try:
                record = run_item(item, client, prompt)
            except (
                RateLimitError,
                APIStatusError,
                APIConnectionError,
                TimeoutError,
            ) as error:
                transient = _is_transient(error)
                retry_after = (
                    _retry_after_seconds(error)
                    if isinstance(error, RateLimitError)
                    else None
                )
                _append_jsonl(
                    attempts_path,
                    {
                        "item_id": item["item_id"],
                        "timestamp": _utc_now(),
                        "attempt": prior_attempt_counts.get(item["item_id"], 0)
                        + attempts,
                        "error_type": type(error).__name__,
                        "status_code": _api_error_status(error),
                        "retry_after_s": retry_after,
                        "transient": transient,
                    },
                )
                if isinstance(error, RateLimitError):
                    if attempts < 3:
                        sleep(
                            max(retry_after, float(attempts))
                            if retry_after is not None
                            else float(attempts)
                        )
                        continue
                    quota_reached = True
                    break
                if transient and retry_api_failures and attempts < 3:
                    sleep(float(attempts))
                    continue
                break

            record.update(
                {
                    "attempts": prior_attempt_counts.get(item["item_id"], 0)
                    + attempts,
                    "model": model,
                    "prompt_version": prompt_version,
                    "prompt_sha256": prompt_sha256,
                }
            )
            _append_jsonl(responses_path, record)
            current_final.append(record)
            final_ids.add(item["item_id"])
            break

        if quota_reached:
            break
        if item_index + 1 < len(batch) and request_delay > 0:
            sleep(request_delay)

    final_rows = _read_jsonl(responses_path)
    final_ids = {row["item_id"] for row in final_rows}
    failed_ids = {
        row["item_id"]
        for row in _read_jsonl(attempts_path)
        if row["item_id"] not in final_ids
    }
    payloads_by_id = {item["item_id"]: item["payload"] for item in selected}
    strict_valid = sum(
        classify_response(row["response_text"], payloads_by_id[row["item_id"]]).valid
        for row in current_final
    )
    print(
        f"Run {run_dir.name}: {len(final_ids)}/{len(selected)} final | "
        f"{len(failed_ids)} pending retry | this batch: {len(current_final)}"
    )
    print(f"Strict-valid this batch: {strict_valid}/{len(current_final)}")
    if quota_reached:
        print(
            "Quota/rate limit reached after "
            f"{len(current_final)} items; run again later"
        )
        return 3
    if len(final_ids) == len(selected):
        print("RUN COMPLETE")
    else:
        print(f"Run the same command again for the next {batch_size}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resumable extraction runner")
    parser.add_argument("--prompt", required=True)
    parser.add_argument(
        "--set", dest="gold_set", choices=("quiz", "organic", "edge", "all"),
        required=True,
    )
    parser.add_argument(
        "--split", choices=("dev", "heldout", "all"), required=True
    )
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--model")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--retry-api-failures", action="store_true")
    parser.add_argument("--new-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return run_invocation(
            prompt_version=args.prompt,
            gold_set=args.gold_set,
            split=args.split,
            batch_size=args.batch_size,
            model=args.model,
            status=args.status,
            dry_run=args.dry_run,
            retry_api_failures=args.retry_api_failures,
            new_run=args.new_run,
        )
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
