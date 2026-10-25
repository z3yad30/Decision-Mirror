from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from decision_mirror.extraction.payloads import build_quiz_payload


ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT / "data" / "gold"
PROCESSED_DIR = ROOT / "data" / "processed"
EVAL_USER = "EVAL_USER"
TRAIT_IDS = tuple(f"T{index:02d}" for index in range(1, 7))
GOLD_FILES = (
    "data/gold/quiz_gold_v1.0.json",
    "data/gold/organic_gold_v1.0.json",
    "data/gold/edge_cases_v1.0.json",
)


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _decision_payload(record_id: str, decision_text: str) -> dict[str, Any]:
    return {
        "decision_id": record_id,
        "user_id": EVAL_USER,
        "source_type": "decision_log",
        "decision_text": decision_text,
        "ontology_version": "v1.0",
        "language": "en",
    }


def _split_for(gold_set: str, record_id: str, split: dict[str, Any]) -> str:
    if record_id in split[gold_set]["heldout"]:
        return "heldout"
    if record_id in split[gold_set]["dev"]:
        return "dev"
    raise ValueError(f"{gold_set} record {record_id} is missing from split_v1.json")


def _quiz_item(record: dict[str, Any], split: dict[str, Any]) -> dict[str, Any]:
    trait_id = record["trait_id"]
    traits = {
        item_trait: (
            {"value": record["gold_value"], "confidence": record["confidence"]}
            if item_trait == trait_id
            else None
        )
        for item_trait in TRAIT_IDS
    }
    payload = build_quiz_payload(
        scenario=record["scenario"],
        answer_text=record["answer_text"],
        question_id=record["question_id"],
        decision_id=record["record_id"],
        user_id=EVAL_USER,
    )
    return {
        "item_id": record["record_id"],
        "gold_set": "quiz",
        "split": _split_for("quiz", record["record_id"], split),
        "payload": payload,
        "gold": {
            "target_trait": trait_id,
            "traits": traits,
            "situational_factor": record["situational_factor"],
            "ambiguous_gold": False,
        },
    }


def _organic_item(record: dict[str, Any], split: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": record["record_id"],
        "gold_set": "organic",
        "split": _split_for("organic", record["record_id"], split),
        "payload": _decision_payload(record["record_id"], record["decision_text"]),
        "gold": {
            "traits": record["gold_traits"],
            "situational_factor": record["gold_situational_factor"],
            "ambiguous_gold": record["ambiguous_gold"],
        },
    }


def _edge_item(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": record["record_id"],
        "gold_set": "edge",
        "split": "dev",
        "payload": _decision_payload(record["record_id"], record["decision_text"]),
        "gold": {
            "traits": {trait_id: None for trait_id in TRAIT_IDS},
            "situational_factor": None,
            "ambiguous_gold": False,
            "expected": record["expected"],
        },
    }


def build_eval_set() -> list[dict[str, Any]]:
    quiz = _read_json(GOLD_DIR / "quiz_gold_v1.0.json")
    organic = _read_json(GOLD_DIR / "organic_gold_v1.0.json")
    edge = _read_json(GOLD_DIR / "edge_cases_v1.0.json")
    split = _read_json(PROCESSED_DIR / "split_v1.json")
    return (
        [_quiz_item(record, split) for record in quiz["records"]]
        + [_organic_item(record, split) for record in organic["records"]]
        + [_edge_item(record) for record in edge["records"]]
    )


def write_manifest(eval_path: Path) -> None:
    files = {
        relative_path: _sha256(ROOT / relative_path)
        for relative_path in GOLD_FILES
    }
    files["data/processed/split_v1.json"] = _sha256(
        PROCESSED_DIR / "split_v1.json"
    )
    files["data/processed/eval_set_v1.json"] = _sha256(eval_path)
    _write_json(
        PROCESSED_DIR / "MANIFEST.json",
        {
            "version": "1.0",
            "hash_algorithm": "SHA-256",
            "files": files,
        },
    )


def main() -> None:
    eval_path = PROCESSED_DIR / "eval_set_v1.json"
    _write_json(eval_path, build_eval_set())
    write_manifest(eval_path)
    print(f"Wrote {eval_path.relative_to(ROOT)}")
    print(f"Wrote {(PROCESSED_DIR / 'MANIFEST.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
