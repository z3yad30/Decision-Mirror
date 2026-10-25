from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "schemas"
    / "extraction_output.schema.json"
)
with _SCHEMA_PATH.open(encoding="utf-8") as schema_file:
    _OUTPUT_SCHEMA = json.load(schema_file)
_OUTPUT_VALIDATOR = Draft7Validator(_OUTPUT_SCHEMA)

_WHITESPACE = re.compile(r"\s+")
_QUOTE_TRANSLATION = str.maketrans(
    {
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u00ab": '"',
        "\u00bb": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u0060": "'",
    }
)


@dataclass
class ValidationOutcome:
    schema_errors: list[str] = field(default_factory=list)
    semantic_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recovered: bool = False
    failure_type: str | None = None
    failure_message: str | None = None
    response: dict[str, Any] | None = None

    @property
    def valid(self) -> bool:
        return not self.schema_errors and not self.semantic_errors and self.failure_type is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_errors": self.schema_errors,
            "semantic_errors": self.semantic_errors,
            "warnings": self.warnings,
        }


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_non_finite(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric value: {value}")


def _strict_json_loads(raw_text: str) -> Any:
    return json.loads(
        raw_text,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_non_finite,
    )


def _recovery_candidate(raw_text: str) -> str | None:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1]).strip()
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    return text if text else None


def _was_recoverable(raw_text: str) -> bool:
    candidate = _recovery_candidate(raw_text)
    if candidate is None or candidate == raw_text.strip():
        return False
    try:
        _strict_json_loads(candidate)
    except (json.JSONDecodeError, ValueError):
        return False
    return True


def _normalize_quote(text: str) -> str:
    return _WHITESPACE.sub(" ", text.translate(_QUOTE_TRANSLATION)).strip()


def _format_schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"{path}: {error.message}"


def _validate_semantics(
    response: dict[str, Any], payload: dict[str, Any]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    traits = response["traits"]

    expected_order = [f"T{index:02d}" for index in range(1, 7)]
    actual_order = [trait["trait_id"] for trait in traits]
    if actual_order != expected_order:
        errors.append(
            f"traits must appear exactly once in T01-T06 order; got {actual_order}"
        )

    scored = [trait["score"] is not None for trait in traits]
    status = response["extraction_status"]
    if status == "success" and not any(scored):
        errors.append("success requires at least one non-null score")
    elif status == "insufficient_evidence" and any(scored):
        errors.append("insufficient_evidence requires all scores to be null")

    text = payload.get("decision_text", "")
    normalized_text = _normalize_quote(text) if isinstance(text, str) else ""
    for trait in traits:
        trait_id = trait["trait_id"]
        score = trait["score"]
        confidence = trait["confidence"]
        evidence = trait["evidence"]

        if score is None:
            if confidence != 0.0:
                errors.append(f"{trait_id}: null score requires confidence 0.0")
            if evidence:
                errors.append(f"{trait_id}: null score requires empty evidence")
            if trait_id != "T06" and not trait["context_notes"].strip():
                errors.append(f"{trait_id}: null score requires an explanatory context_notes")
        elif not evidence:
            errors.append(f"{trait_id}: non-null score requires at least one evidence quote")
        elif confidence < 0.2:
            warnings.append(
                f"low_confidence: {trait_id} has a non-null score and confidence below 0.2"
            )

        for evidence_index, quote in enumerate(evidence, 1):
            if _normalize_quote(quote) not in normalized_text:
                warnings.append(
                    f"evidence_not_grounded: {trait_id} evidence item {evidence_index} "
                    "was not found in decision_text after normalization"
                )

        factor = trait["situational_factor"]
        if factor is not None:
            notes = _normalize_quote(trait["context_notes"]).casefold()
            category_text = factor["category"].replace("_", " ").casefold()
            category_code = factor["category"].casefold()
            description = _normalize_quote(factor["description"]).casefold()
            if not (
                category_text in notes
                or category_code in notes
                or (description and description in notes)
            ):
                warnings.append(
                    f"situational_factor_not_in_notes: {trait_id} context_notes "
                    "does not mention its situational factor"
                )

    context = payload.get("context")
    history = context.get("history") if isinstance(context, dict) else None
    if not history and traits[5]["score"] is not None:
        errors.append("T06 score must be null when context.history is absent or empty")

    if response["decision_id"] != payload.get("decision_id"):
        errors.append("response decision_id must equal input decision_id")
    return errors, warnings


def classify_response(raw_text: str, payload: dict[str, Any]) -> ValidationOutcome:
    """Strictly classify one model response; recovered text is diagnostic only."""
    if not raw_text.strip():
        return ValidationOutcome(failure_type="empty_response")

    try:
        response = _strict_json_loads(raw_text)
    except (json.JSONDecodeError, ValueError):
        return ValidationOutcome(
            recovered=_was_recoverable(raw_text),
            failure_type="not_json",
        )

    schema_errors = sorted(
        (_format_schema_error(error) for error in _OUTPUT_VALIDATOR.iter_errors(response))
    )
    if schema_errors:
        return ValidationOutcome(
            schema_errors=schema_errors,
            failure_type="schema_violation",
        )

    semantic_errors, warnings = _validate_semantics(response, payload)
    if semantic_errors:
        return ValidationOutcome(
            semantic_errors=semantic_errors,
            warnings=warnings,
            failure_type="semantic_violation",
        )
    return ValidationOutcome(warnings=warnings, response=response)


def classify_api_error(error: Exception) -> ValidationOutcome:
    """Represent an upstream API failure without pretending it was model output."""
    return ValidationOutcome(
        failure_type="api_error",
        failure_message=f"{type(error).__name__}: {error}",
    )
