import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from decision_mirror.common.models import ExtractionOutput, TraitObservation


ROOT = Path(__file__).resolve().parents[1]
VALID_DIR = ROOT / "schemas" / "examples" / "valid"
INVALID_DIR = ROOT / "schemas" / "examples" / "invalid"


@pytest.mark.parametrize("fixture_path", sorted(VALID_DIR.glob("*.json")))
def test_valid_fixture_round_trips(fixture_path):
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    model = ExtractionOutput.model_validate(fixture["response"])
    assert model.model_dump(mode="json") == fixture["response"]


@pytest.mark.parametrize("fixture_path", sorted(INVALID_DIR.glob("*.json")))
def test_invalid_fixture_is_rejected(fixture_path):
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    raw_text = fixture.get("raw_text")
    body = raw_text if raw_text is not None else fixture.get("response")
    if body is None:
        raise AssertionError(f"{fixture_path.name} has no response body")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return
    try:
        ExtractionOutput.model_validate(body)
    except ValidationError:
        pass
    else:
        raise AssertionError(f"{fixture_path.name} was accepted")


def observation_data(**changes):
    data = {
        "trait_id": "T01",
        "score": 0.5,
        "confidence": 0.8,
        "evidence": ["I chose the careful option"],
        "situational_factor": None,
        "context_notes": "",
        "source": "decision",
    }
    data.update(changes)
    return data


def test_null_score_requires_zero_confidence_and_empty_evidence():
    with pytest.raises(ValidationError):
        TraitObservation.model_validate(
            observation_data(score=None, confidence=0.4, evidence=["unsupported"])
        )
    model = TraitObservation.model_validate(
        observation_data(score=None, confidence=0.0, evidence=[], context_notes="No support")
    )
    assert model.score is None


def test_non_null_score_requires_evidence():
    with pytest.raises(ValidationError):
        TraitObservation.model_validate(observation_data(evidence=[]))


def test_unknown_field_is_rejected():
    with pytest.raises(ValidationError):
        TraitObservation.model_validate(observation_data(gold_value=0.9))


def test_wrong_trait_id_is_rejected():
    with pytest.raises(ValidationError):
        TraitObservation.model_validate(observation_data(trait_id="T99"))


def test_extraction_status_consistency():
    fixture = json.loads(
        (VALID_DIR / "t06_null_without_history.json").read_text(encoding="utf-8")
    )
    success = fixture["response"]
    success["extraction_status"] = "insufficient_evidence"
    with pytest.raises(ValidationError):
        ExtractionOutput.model_validate(success)
