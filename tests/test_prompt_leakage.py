import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT / "data" / "gold"
PROMPT_PATH = ROOT / "prompts" / "extraction" / "extraction_v2.0.md"
_WHITESPACE = re.compile(r"\s+")
_QUOTE_TRANSLATION = str.maketrans(
    {
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
    }
)
_D001_SENTENCE = (
    "I rejected a startup position because I couldn't risk losing my current income."
)


def normalize(text):
    return _WHITESPACE.sub(" ", text.translate(_QUOTE_TRANSLATION)).strip().casefold()


def read_gold_files():
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(GOLD_DIR.glob("*.json"))
    ]


def walk(value, parent_key=""):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield from walk(nested, key)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested, parent_key)
    elif isinstance(value, str):
        yield parent_key, value


def test_prompt_contains_no_gold_text_or_ids():
    prompt = normalize(PROMPT_PATH.read_text(encoding="utf-8"))
    gold_files = read_gold_files()
    leakage_candidates = []
    record_ids = []

    for gold in gold_files:
        for key, text in walk(gold):
            if key in {"scenario", "answer_text", "decision_text"}:
                leakage_candidates.append(text)
            if key == "evidence" or key.endswith("_evidence"):
                leakage_candidates.append(text)
            if key == "record_id":
                record_ids.append(text)

    leakage_candidates.append(_D001_SENTENCE)
    for candidate in leakage_candidates:
        normalized_candidate = normalize(candidate)
        if normalized_candidate:
            assert normalized_candidate not in prompt, (
                f"prompt contains gold text: {candidate}"
            )

    for record_id in record_ids:
        assert normalize(record_id) not in prompt


def test_prompt_has_required_trait_ids_names_statuses_and_bands():
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    for trait_id, name in (
        ("T01", "Risk Tolerance"),
        ("T02", "Time Horizon"),
        ("T03", "Locus of Priority"),
        ("T04", "Decisiveness Speed"),
        ("T05", "Emotional vs. Analytical Weighting"),
        ("T06", "Self-Consistency"),
    ):
        assert trait_id in prompt
        assert name in prompt

    assert '"success"' in prompt
    assert '"insufficient_evidence"' in prompt
    assert "[0.0,0.2)" in prompt
    assert "[0.2,0.4)" in prompt
    assert "[0.4,0.6)" in prompt
    assert "[0.6,0.8)" in prompt
    assert "[0.8,1.0]" in prompt
