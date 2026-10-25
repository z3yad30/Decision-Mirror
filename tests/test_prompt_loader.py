import hashlib
import json
from pathlib import Path

import pytest

from decision_mirror.extraction import prompt_loader


ROOT = Path(__file__).resolve().parents[1]


def test_load_prompt_returns_text_and_sha256():
    text, sha256 = prompt_loader.load_prompt("v2.0")
    prompt_path = ROOT / "prompts" / "extraction" / "extraction_v2.0.md"

    assert text == prompt_path.read_bytes().decode("utf-8")
    assert sha256 == hashlib.sha256(prompt_path.read_bytes()).hexdigest()


def test_frozen_prompt_hash_is_verified(tmp_path, monkeypatch):
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()
    prompt_path = prompt_dir / "frozen.md"
    prompt_path.write_text("frozen prompt", encoding="utf-8")
    registry_path = prompt_dir / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "prompts": [
                    {
                        "version": "v9.0",
                        "file": "frozen.md",
                        "sha256": "0" * 64,
                        "status": "frozen",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(prompt_loader, "_PROMPTS_DIR", prompt_dir)
    monkeypatch.setattr(prompt_loader, "_REGISTRY_PATH", registry_path)

    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        prompt_loader.load_prompt("v9.0")

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["prompts"][0]["sha256"] = hashlib.sha256(
        prompt_path.read_bytes()
    ).hexdigest()
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    assert prompt_loader.load_prompt("v9.0") == (
        "frozen prompt",
        hashlib.sha256(prompt_path.read_bytes()).hexdigest(),
    )


def test_legacy_prompt_is_refused_without_opt_in():
    with pytest.raises(ValueError, match="allow_legacy=True"):
        prompt_loader.load_prompt("v1.0")

    text, sha256 = prompt_loader.load_prompt("v1.0", allow_legacy=True)
    assert text
    assert len(sha256) == 64


def test_unknown_prompt_version_raises():
    with pytest.raises(ValueError, match="unknown extraction prompt version"):
        prompt_loader.load_prompt("v99.0")
