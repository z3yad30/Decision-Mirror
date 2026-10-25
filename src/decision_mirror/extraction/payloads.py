from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


MODEL_REQUEST_FIELDS = (
    "decision_id",
    "source_type",
    "decision_text",
    "ontology_version",
    "language",
)
_INPUT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "schemas"
    / "extraction_input.schema.json"
)
with _INPUT_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
    _INPUT_VALIDATOR = Draft7Validator(json.load(schema_file))


def build_quiz_payload(
    scenario: str,
    answer_text: str,
    question_id: str,
    decision_id: str,
    user_id: str,
) -> dict[str, Any]:
    """Build the Task 4 input using only the quiz scenario and selected answer."""
    return {
        "decision_id": decision_id,
        "user_id": user_id,
        "source_type": "onboarding_quiz",
        "decision_text": f"Scenario: {scenario}\nSelected answer: {answer_text}",
        "ontology_version": "v1.0",
        "language": "en",
        "context": {
            "question_id": question_id,
        },
    }


def build_model_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Return only fields permitted in the LLM request."""
    _INPUT_VALIDATOR.validate(payload)
    request = {
        key: payload[key]
        for key in MODEL_REQUEST_FIELDS
        if key in payload
    }
    context = payload.get("context")
    if isinstance(context, dict) and "history" in context:
        request["context"] = {"history": context["history"]}
    return request
