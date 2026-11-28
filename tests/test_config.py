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


def test_shift_window_requires_one_decision():
    with pytest.raises(ValidationError):
        Settings(shift_window=0)
    assert Settings(shift_window=1).shift_window == 1


def test_recency_half_life_accepts_none_and_positive():
    assert Settings(recency_half_life_days=None).recency_half_life_days is None
    assert Settings(recency_half_life_days=30).recency_half_life_days == 30


@pytest.mark.parametrize("value", [0, -1, -30])
def test_recency_half_life_rejects_non_positive_numbers(value):
    with pytest.raises(ValidationError):
        Settings(recency_half_life_days=value)


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
