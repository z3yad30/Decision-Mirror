from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

from decision_mirror.extraction.llm_client import LLMClient
from decision_mirror.extraction.payloads import build_model_request


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
