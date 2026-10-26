from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from decision_mirror.extraction import validation

from evaluation.metrics import SEVERITY_ORDER, analyze_items


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "evaluation" / "runs"
RESULTS_DIR = ROOT / "evaluation" / "results"
EVAL_SET_PATH = ROOT / "data" / "processed" / "eval_set_v1.json"
ORGANIC_GOLD_PATH = ROOT / "data" / "gold" / "organic_gold_v1.0.json"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"required run file does not exist: {path}")
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"invalid JSONL in {path} at line {line_number}"
            ) from error
        if not isinstance(row, dict):
            raise ValueError(f"expected JSON object at {path}:{line_number}")
        rows.append(row)
    return rows


def _json_write(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _jsonl_write(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(
                json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
            )


def _load_run(
    run_id: str,
    *,
    runs_dir: Path,
    eval_set_path: Path,
    organic_gold_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    run_dir = runs_dir / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run directory not found: {run_dir}")
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"run manifest not found: {manifest_path}")
    manifest = _read_json(manifest_path)
    raw_path = run_dir / "raw_responses.jsonl"
    raw_rows = _read_jsonl(raw_path)
    items = _read_json(eval_set_path)
    if manifest.get("eval_set_sha256") != hashlib.sha256(
        eval_set_path.read_bytes()
    ).hexdigest():
        raise ValueError(
            f"evaluation-set hash mismatch for {run_id}; use the original "
            "eval_set_v1.json associated with this run"
        )
    gold_set = manifest.get("set", "all")
    split = manifest.get("split", "all")
    selected = [
        item for item in items
        if (gold_set == "all" or item["gold_set"] == gold_set)
        and (split == "all" or item["split"] == split)
    ]
    organic_gold = _read_json(organic_gold_path)
    organic_evidence = {
        row["record_id"]: row.get("gold_evidence", [])
        for row in organic_gold["records"]
    }
    for item in selected:
        if item["gold_set"] == "organic":
            item["gold"]["evidence"] = organic_evidence.get(item["item_id"], [])
    return manifest, selected, raw_rows


def evaluate_run(
    run_id: str,
    *,
    runs_dir: Path | None = None,
    results_dir: Path | None = None,
    eval_set_path: Path | None = None,
    organic_gold_path: Path | None = None,
) -> dict[str, Any]:
    runs_dir = runs_dir or RUNS_DIR
    results_dir = results_dir or RESULTS_DIR
    eval_set_path = eval_set_path or EVAL_SET_PATH
    organic_gold_path = organic_gold_path or ORGANIC_GOLD_PATH
    manifest, items, raw_rows = _load_run(
        run_id,
        runs_dir=runs_dir,
        eval_set_path=eval_set_path,
        organic_gold_path=organic_gold_path,
    )
    analysis = analyze_items(items, raw_rows, validation)
    metrics = analysis["metrics"]
    metrics["run"] = {
        "run_id": run_id,
        "prompt_version": manifest.get("prompt_version"),
        "prompt_sha256": manifest.get("prompt_sha256"),
        "model": manifest.get("model"),
        "temperature": manifest.get("temperature"),
        "max_completion_tokens": manifest.get("max_completion_tokens"),
        "reasoning_effort": manifest.get("reasoning_effort"),
        "response_format": manifest.get("response_format"),
        "created_at": manifest.get("created_at"),
        "split": manifest.get("split"),
        "set": manifest.get("set", "all"),
        "batch_size": manifest.get("batch_size"),
        "eval_set_sha256": manifest.get("eval_set_sha256"),
        "raw_response_count": len(raw_rows),
    }
    destination = results_dir / run_id
    destination.mkdir(parents=True, exist_ok=True)
    _json_write(destination / "metrics.json", metrics)
    _write_per_item_csv(destination / "per_item.csv", analysis["items"])
    _jsonl_write(destination / "error_log.jsonl", analysis["errors"])
    _json_write(
        destination / "schema_compliance.json",
        {
            "summary": metrics["format"],
            "items": analysis["compliance"],
        },
    )
    (destination / "tables.md").write_text(
        _render_tables(metrics), encoding="utf-8", newline="\n"
    )
    (destination / "difficult_cases.md").write_text(
        _render_difficult_cases(analysis), encoding="utf-8", newline="\n"
    )
    return analysis


def _write_per_item_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "item_id",
        "gold_set",
        "split",
        "target_trait",
        "strict_json_parse",
        "schema_valid",
        "semantic_valid",
        "recovered",
        "failure_type",
        "gold_status",
        "model_status",
        "score_errors",
        *(f"gold_score_T{index:02d}" for index in range(1, 7)),
        *(f"gold_confidence_T{index:02d}" for index in range(1, 7)),
        *(f"score_T{index:02d}" for index in range(1, 7)),
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _percent(value: Any) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def _number(value: Any) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def _render_tables(metrics: dict[str, Any]) -> str:
    lines = [
        "# Evaluation tables",
        "",
        "## Format compliance",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in (
        "strict_json_parse_rate",
        "schema_valid_rate",
        "semantic_valid_rate",
        "recovered_rate",
    ):
        lines.append(f"| {key} | {_percent(metrics['format'][key])} |")
    lines.extend(["", "## Quiz target-trait scoring", ""])
    quiz = metrics["quiz"]["target_trait_scoring"]
    lines.extend(
        [
            "| Trait | N | Non-null | MAE | Exact band | Within one | QWK | Spearman | Direction | Inversions |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for trait_id in (*[f"T{i:02d}" for i in range(1, 6)], "overall"):
        row = quiz[trait_id]
        lines.append(
            f"| {trait_id} | {row['n_paired_scores']} | "
            f"{_percent(row['target_non_null_rate'])} | {_number(row['mae'])} | "
            f"{_percent(row['exact_band_accuracy'])} | "
            f"{_percent(row['within_one_band_rate'])} | "
            f"{_number(row['quadratic_weighted_kappa'])} | "
            f"{_number(row['spearman_rho'])} | "
            f"{_percent(row['direction_accuracy'])} | {row['polarity_inversions']} |"
        )
    lines.extend(["", "## Quiz confusion matrix (overall)", ""])
    confusion = quiz["overall"]["confusion_matrix_5x5"]
    lines.extend(
        [
            "| Gold band / predicted band | " + " | ".join(str(index) for index in range(5)) + " |",
            "|---|" + "---:|" * 5,
        ]
    )
    for index, counts in enumerate(confusion):
        lines.append(f"| {index} | " + " | ".join(map(str, counts)) + " |")
    lines.extend(["", "## Quiz 95% bootstrap confidence intervals", ""])
    lines.extend(
        [
            "| Trait | MAE | Exact band accuracy | Spearman rho |",
            "|---|---|---|---|",
        ]
    )
    for trait_id in (*[f"T{i:02d}" for i in range(1, 6)], "overall"):
        intervals = quiz[trait_id]["bootstrap_95_ci"]

        def render_ci(name: str) -> str:
            interval = intervals[name]
            if interval["lower"] is None:
                return "n/a"
            return f"[{interval['lower']:.3f}, {interval['upper']:.3f}] (n={interval['n']})"

        lines.append(
            f"| {trait_id} | {render_ci('mae')} | {render_ci('accuracy')} | "
            f"{render_ci('rho')} |"
        )
    lines.extend(["", "## Organic metrics", ""])
    organic = metrics["organic"]["score_metrics"]["overall"]
    lines.extend(
        [
            "| Metric | Value |",
            "|---|---:|",
            f"| Paired numeric scores | {organic['n_paired_scores']} |",
            f"| MAE | {_number(organic['mae'])} |",
            f"| Exact band accuracy | {_percent(organic['exact_band_accuracy'])} |",
            f"| Missed-signal rate | {_percent(organic['missed_signal_rate'])} |",
            f"| Unsupported-inference rate | {_percent(organic['unsupported_inference_rate'])} |",
            f"| Status accuracy | {_percent(organic['status_accuracy'])} |",
            f"| Situational-factor precision | {_percent(organic['situational_factor']['precision'])} |",
            f"| Situational-factor recall | {_percent(organic['situational_factor']['recall'])} |",
            f"| Situational-factor category agreement | {_percent(organic['situational_factor']['category_agreement'])} |",
            f"| Confidence MAE (unambiguous gold) | {_number(organic['confidence_mae'])} |",
            f"| Evidence token-overlap F1 (report only) | {_number(organic['organic_evidence_token_overlap_f1_report_only'])} |",
            "",
            "## Evidence, edge cases, and readiness",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Evidence grounding | {_percent(metrics['evidence']['grounding_rate'])} |",
            f"| Edge-case checks | {metrics['edge_cases']['passed_checks']}/{metrics['edge_cases']['total_checks']} ({_percent(metrics['edge_cases']['pass_rate'])}) |",
            f"| T06 violations | {metrics['t06_violations']['count']} |",
            "",
            "Readiness thresholds are proposed and pending team lead approval.",
            "",
            "| Criterion | Observed | Threshold | Result |",
            "|---|---:|---:|---|",
        ]
    )
    for name, result in metrics["readiness_criteria"].items():
        observed = result["observed"]
        rate_names = {
            "strict_schema_valid_rate",
            "schema_valid_or_recovered_rate",
            "quiz_target_non_null_rate",
            "quiz_exact_band_accuracy",
            "quiz_within_one_band_rate",
            "quiz_direction_accuracy",
            "quiz_polarity_inversion_rate",
            "evidence_grounding_rate",
            "edge_case_pass_rate",
            "organic_situational_factor_recall",
        }
        rendered = _percent(observed) if name in rate_names else _number(observed)
        threshold = result["threshold"]
        rendered_threshold = (
            _percent(threshold) if name in rate_names else str(threshold)
        )
        lines.append(
            f"| {name} | {rendered} | {result['operator']} {rendered_threshold} | {result['status']} |"
        )
    return "\n".join(lines) + "\n"


def _render_difficult_cases(analysis: dict[str, Any]) -> str:
    errors = sorted(
        analysis["errors"],
        key=lambda error: (
            SEVERITY_ORDER.get(error["severity"], 9),
            error["item_id"],
            error["error_type"],
        ),
    )
    lines = ["# Difficult cases", ""]
    if not errors:
        lines.append("No automated errors or manual-review flags were produced.")
    else:
        lines.extend(
            [
                "| Item | Severity | Error type | Expected | Actual | Notes |",
                "|---|---|---|---|---|---|",
            ]
        )
        for error in errors:
            expected = json.dumps(error["expected"], ensure_ascii=False)
            actual = json.dumps(error["actual"], ensure_ascii=False)
            notes = error["notes"].replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {error['item_id']} | {error['severity']} | "
                f"{error['error_type']} | `{expected}` | `{actual}` | {notes} |"
            )
    lines.extend(["", "## Cross-review sample", ""])
    sample = analysis["metrics"]["manual_review_sample"]
    lines.append(
        "Items below matched the numeric gold band and are flagged for human "
        "evidence-support review; score agreement alone is not evidence quality."
    )
    lines.extend(["", *[f"- `{item_id}`" for item_id in sample]])
    lines.extend(["", "## Ambiguous organic gold", ""])
    ambiguous = analysis["metrics"]["organic"]["ambiguous_gold_separate"]
    if ambiguous:
        lines.extend(f"- `{item['item_id']}`: reported separately, excluded from headline metrics." for item in ambiguous)
    else:
        lines.append("No ambiguous organic gold items in this run.")
    return "\n".join(lines) + "\n"
