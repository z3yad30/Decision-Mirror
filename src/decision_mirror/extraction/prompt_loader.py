from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


_PROMPTS_DIR = (
    Path(__file__).resolve().parents[3] / "prompts" / "extraction"
)
_REGISTRY_PATH = _PROMPTS_DIR / "registry.json"


def load_prompt(version: str, *, allow_legacy: bool = False) -> tuple[str, str]:
    """Load a registered extraction prompt and return its text and SHA-256."""
    registry: dict[str, Any] = json.loads(
        _REGISTRY_PATH.read_text(encoding="utf-8")
    )
    entries = {entry["version"]: entry for entry in registry["prompts"]}
    if version not in entries:
        raise ValueError(f"unknown extraction prompt version: {version}")

    entry = entries[version]
    if entry["status"] == "legacy" and not allow_legacy:
        raise ValueError(
            f"legacy extraction prompt {version} requires allow_legacy=True"
        )

    prompt_path = _PROMPTS_DIR / entry["file"]
    prompt_bytes = prompt_path.read_bytes()
    sha256 = hashlib.sha256(prompt_bytes).hexdigest()
    if entry["status"] == "frozen" and sha256 != entry["sha256"]:
        raise RuntimeError(
            f"SHA-256 mismatch for frozen extraction prompt {version}"
        )
    return prompt_bytes.decode("utf-8"), sha256
