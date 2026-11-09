from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_run_script", ROOT / "scripts" / "evaluate_run.py"
)
assert SPEC is not None and SPEC.loader is not None
evaluate_run_script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluate_run_script)


@pytest.mark.parametrize("split", ["heldout", "all"])
def test_unfrozen_heldout_prompt_emits_loud_warning(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], split: str
) -> None:
    monkeypatch.setattr(
        evaluate_run_script, "get_prompt_status", lambda version: "draft"
    )

    evaluate_run_script._warn_if_unfrozen_heldout(
        {"split": split, "prompt_version": "v2.1"}
    )

    warning = capsys.readouterr().err
    assert "WARNING: HELD-OUT EVALUATION" in warning
    assert "version='v2.1'" in warning
    assert "registry_status='draft'" in warning


def test_frozen_heldout_prompt_and_dev_prompt_do_not_warn(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        evaluate_run_script, "get_prompt_status", lambda version: "frozen"
    )

    evaluate_run_script._warn_if_unfrozen_heldout(
        {"split": "heldout", "prompt_version": "v2.0"}
    )
    evaluate_run_script._warn_if_unfrozen_heldout(
        {"split": "dev", "prompt_version": "v2.1"}
    )

    assert capsys.readouterr().err == ""
