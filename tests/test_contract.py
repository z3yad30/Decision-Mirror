import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator, ValidationError, validate

from decision_mirror.extraction.payloads import (
    build_model_request,
    build_quiz_payload,
)
from decision_mirror.extraction.validation import classify_response


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = SCHEMAS / "examples"


def read_schema(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def fixture_cases(folder):
    return sorted((EXAMPLES / folder).glob("*.json"))


def test_example_folders_have_the_required_minimum_cases():
    assert len(fixture_cases("valid")) >= 6
    assert len(fixture_cases("invalid")) >= 14


@pytest.mark.parametrize("schema_name", [
    "extraction_input.schema.json",
    "extraction_output.schema.json",
    "extraction_result.schema.json",
])
def test_schemas_are_valid_draft_07(schema_name):
    Draft7Validator.check_schema(read_schema(schema_name))


def test_result_schema_accepts_success_and_pipeline_error_envelopes():
    example = json.loads(
        (EXAMPLES / "valid" / "fully_scored_narrative.json").read_text(
            encoding="utf-8"
        )
    )
    base = {
        "decision_id": "D001",
        "model_version": "model-1",
        "prompt_version": "v1.0",
        "prompt_sha256": "a" * 64,
        "validation": {
            "schema_valid": True,
            "semantic_valid": True,
            "warnings": [],
        },
    }
    schema = read_schema("extraction_result.schema.json")
    validate(
        {
            **base,
            "extraction_status": "success",
            "traits": example["response"]["traits"],
            "error": None,
        },
        schema,
    )
    validate(
        {
            **base,
            "extraction_status": "error",
            "traits": None,
            "error": {"type": "not_json", "message": "Response was not JSON."},
            "validation": {
                "schema_valid": False,
                "semantic_valid": False,
                "warnings": [],
            },
        },
        schema,
    )


@pytest.mark.parametrize("example_path", fixture_cases("valid"), ids=lambda path: path.stem)
def test_valid_examples_pass_schema_and_semantics(example_path):
    example = json.loads(example_path.read_text(encoding="utf-8"))
    outcome = classify_response(
        json.dumps(example["response"]),
        example["payload"],
    )
    assert outcome.failure_type is None
    assert outcome.valid
    assert outcome.response == example["response"]


@pytest.mark.parametrize("example_path", fixture_cases("invalid"), ids=lambda path: path.stem)
def test_invalid_examples_are_classified(example_path):
    example = json.loads(example_path.read_text(encoding="utf-8"))
    raw_text = example.get("raw_text")
    if raw_text is None:
        raw_text = json.dumps(example["response"])

    outcome = classify_response(raw_text, example["payload"])

    assert outcome.failure_type == example["expected_error_type"]
    assert not outcome.valid
    assert outcome.response is None
    if "expected_recovered" in example:
        assert outcome.recovered is example["expected_recovered"]


def test_input_schema_accepts_short_nonempty_decision_text():
    payload = {
        "decision_id": "decision-1",
        "user_id": "user-1",
        "source_type": "decision_log",
        "decision_text": "I chose option A.",
        "ontology_version": "v1.0",
    }
    validate(payload, read_schema("extraction_input.schema.json"))


def test_input_schema_enforces_trimmed_text_length():
    schema = read_schema("extraction_input.schema.json")
    payload = {
        "decision_id": "decision-1",
        "user_id": "user-1",
        "source_type": "decision_log",
        "decision_text": " " + "x" * 4000 + " ",
        "ontology_version": "v1.0",
    }
    validate(payload, schema)
    payload["decision_text"] = "x" * 4001
    with pytest.raises(ValidationError):
        validate(payload, schema)


@pytest.mark.parametrize("mutate", [
    lambda value: value.update(ontology_version="YOUR_ONTOLOGY_VERSION"),
    lambda value: value.update(unexpected="gold"),
    lambda value: value.update(decision_text="   \n "),
])
def test_input_schema_rejects_invalid_version_unknown_fields_and_empty_text(mutate):
    payload = {
        "decision_id": "decision-1",
        "user_id": "user-1",
        "source_type": "decision_log",
        "decision_text": "I chose option A.",
        "ontology_version": "v1.0",
    }
    mutate(payload)
    with pytest.raises(ValidationError):
        validate(payload, read_schema("extraction_input.schema.json"))


def test_input_schema_rejects_question_id_for_decision_log():
    payload = {
        "decision_id": "decision-1",
        "user_id": "user-1",
        "source_type": "decision_log",
        "decision_text": "I chose option A.",
        "ontology_version": "v1.0",
        "context": {"question_id": "question-1"},
    }
    with pytest.raises(ValidationError):
        validate(payload, read_schema("extraction_input.schema.json"))


def test_quiz_payload_uses_only_scenario_and_selected_answer():
    payload = build_quiz_payload(
        scenario="A stable role or an uncertain startup.",
        answer_text="I chose the stable role.",
        question_id="Q01",
        decision_id="D01",
        user_id="U01",
    )
    assert payload == {
        "decision_id": "D01",
        "user_id": "U01",
        "source_type": "onboarding_quiz",
        "decision_text": (
            "Scenario: A stable role or an uncertain startup.\n"
            "Selected answer: I chose the stable role."
        ),
        "ontology_version": "v1.0",
        "language": "en",
        "context": {"question_id": "Q01"},
    }
    assert not {
        "trait_id",
        "gold_value",
        "evidence",
        "confidence",
        "other_options",
    }.intersection(payload)


def test_model_request_excludes_application_only_fields():
    payload = {
        "decision_id": "D01",
        "user_id": "U01",
        "source_type": "onboarding_quiz",
        "decision_text": "I chose the stable role.",
        "ontology_version": "v1.0",
        "language": "en",
        "timestamp": "2026-10-25T00:00:00Z",
        "context": {
            "question_id": "Q01",
            "history": [{"decision_id": "prior"}],
        },
    }
    assert build_model_request(payload) == {
        "decision_id": "D01",
        "source_type": "onboarding_quiz",
        "decision_text": "I chose the stable role.",
        "ontology_version": "v1.0",
        "language": "en",
        "context": {"history": [{"decision_id": "prior"}]},
    }
    payload["gold_value"] = 0.9
    with pytest.raises(ValidationError):
        build_model_request(payload)


def test_classifier_flags_recovered_fenced_json_without_using_it():
    example = json.loads(
        (EXAMPLES / "invalid" / "markdown_fenced_json.json").read_text(
            encoding="utf-8"
        )
    )
    outcome = classify_response(example["raw_text"], example["payload"])
    assert outcome.failure_type == "not_json"
    assert outcome.recovered
    assert outcome.response is None


def test_empty_response_has_distinct_failure_type():
    outcome = classify_response(" \n ", {"decision_id": "D01"})
    assert outcome.failure_type == "empty_response"


def test_decision_id_mismatch_is_semantic_and_never_returns_data():
    example = json.loads(
        (EXAMPLES / "valid" / "fully_scored_narrative.json").read_text(
            encoding="utf-8"
        )
    )
    example["response"]["decision_id"] = "D999"
    outcome = classify_response(json.dumps(example["response"]), example["payload"])
    assert outcome.failure_type == "semantic_violation"
    assert outcome.response is None


def test_api_error_is_not_reported_as_a_semantic_error():
    from decision_mirror.extraction.validation import classify_api_error

    outcome = classify_api_error(RuntimeError("service unavailable"))
    assert outcome.failure_type == "api_error"
    assert outcome.failure_message == "RuntimeError: service unavailable"
    assert not outcome.semantic_errors


def test_semantic_warnings_do_not_reject_a_valid_response():
    example = json.loads(
        (EXAMPLES / "valid" / "fully_scored_narrative.json").read_text(
            encoding="utf-8"
        )
    )
    payload = example["payload"]
    response = example["response"]
    payload["decision_text"] = payload["decision_text"].replace(
        "predictable income", "“predictable income”"
    )
    response["traits"][0]["evidence"] = [
        'I chose the startup after comparing both offers for a week because its long-term growth and greater autonomy outweighed "predictable income"'
    ]
    response["traits"][0]["confidence"] = 0.1
    response["traits"][0]["situational_factor"] = {
        "category": "financial_dependency",
        "description": "short-term family obligations",
    }
    response["traits"][0]["context_notes"] = "The note does not name that factor."

    outcome = classify_response(json.dumps(response), payload)

    assert outcome.valid
    assert any(warning.startswith("low_confidence:") for warning in outcome.warnings)
    assert any(
        warning.startswith("situational_factor_not_in_notes:")
        for warning in outcome.warnings
    )
    assert not any(
        warning.startswith("evidence_not_grounded:")
        for warning in outcome.warnings
    )
