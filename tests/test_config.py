import pytest
from pydantic import ValidationError

from decision_mirror.common.config import Settings


def test_defaults():
    settings = Settings()
    assert settings.t06_min_usable == 4
    assert settings.t06_strong_at == 8
    assert settings.reminder_days == 7
    assert settings.situational_weight == 0.5
    assert settings.quiz_weight == 0.5
    assert settings.quiz_confidence == 0.30
    assert settings.recency_half_life_days is None
    assert settings.shift_window == 4
    assert settings.shift_threshold == 0.15


def test_environment_override(monkeypatch):
    monkeypatch.setenv("DM_REMINDER_DAYS", "14")
    assert Settings().reminder_days == 14


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("DM_REMINDER_DAYS", "-1"),
        ("DM_SITUATIONAL_WEIGHT", "1.1"),
        ("DM_QUIZ_CONFIDENCE", "-0.1"),
        ("DM_RECENCY_HALF_LIFE_DAYS", "-2"),
        ("DM_SHIFT_THRESHOLD", "1.5"),
    ],
)
def test_invalid_override_is_rejected(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        Settings()
