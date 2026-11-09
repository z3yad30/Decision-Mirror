from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

from decision_mirror.extraction.llm_client import LLMClient
from decision_mirror.extraction.payloads import build_model_request
from decision_mirror.extraction.validation import ValidationOutcome


def _assert_no_gold_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            assert "gold" not in key.casefold(), (
                f"gold-like key reached model request: {key}"
            )
            _assert_no_gold_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_no_gold_keys(nested)


def run_item(
    item: dict[str, Any], client: LLMClient, prompt: str
) -> dict[str, Any]:
    """Call the model once for an evaluation item without parsing its output."""
    request = build_model_request(item["payload"])
    _assert_no_gold_keys(request)
    request_sha256 = hashlib.sha256(
        json.dumps(
            {"prompt": prompt, "request": request},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    started = time.perf_counter()
    completion = client.complete(prompt, request)
    latency_s = time.perf_counter() - started
    return {
        "item_id": item["item_id"],
        "response_text": completion.content,
        "reasoning_text": completion.reasoning_text,
        "finish_reason": completion.finish_reason,
        "usage": completion.usage,
        "latency_s": latency_s,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_sha256": request_sha256,
    }


def build_result_envelope(
    raw_completion: dict[str, Any],
    payload: dict[str, Any],
    outcome: ValidationOutcome,
) -> dict[str, Any]:
    """Build the frozen pipeline-result envelope for one completion or API error."""
    for field in ("model", "prompt_version", "prompt_sha256"):
        if not isinstance(raw_completion.get(field), str) or not raw_completion[field]:
            raise ValueError(f"raw completion is missing {field}")

    failure_type = outcome.failure_type
    if outcome.valid and outcome.response is not None:
        extraction_status = outcome.response["extraction_status"]
        traits = outcome.response["traits"]
        error = None
    else:
        if failure_type is None:
            raise ValueError("invalid validation outcome has no failure type")
        message = outcome.failure_message
        if not message:
            details = outcome.schema_errors or outcome.semantic_errors
            message = "; ".join(details) if details else failure_type
        extraction_status = "error"
        traits = None
        error = {"type": failure_type, "message": message}

    return {
        "decision_id": payload["decision_id"],
        "extraction_status": extraction_status,
        "traits": traits,
        "model_version": raw_completion["model"],
        "prompt_version": raw_completion["prompt_version"],
        "prompt_sha256": raw_completion["prompt_sha256"],
        "error": error,
        "validation": {
            "schema_valid": failure_type
            not in {"empty_response", "not_json", "schema_violation", "api_error"},
            "semantic_valid": outcome.valid,
            "warnings": list(outcome.warnings),
        },
    }
