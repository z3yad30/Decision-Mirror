import hashlib
import json
import runpy
from pathlib import Path

from jsonschema import Draft7Validator

from decision_mirror.extraction.payloads import build_quiz_payload


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TRAIT_IDS = [f"T{index:02d}" for index in range(1, 7)]
BANNED_KEYS = {"trait_id", "evidence"}
build_eval_set = runpy.run_path(
    str(ROOT / "scripts" / "build_eval_set.py")
)["build_eval_set"]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_no_answer_fields(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered_key = key.lower()
            assert not lowered_key.startswith("gold")
            assert lowered_key not in BANNED_KEYS
            assert lowered_key != "trait_id"
            assert lowered_key != "evidence"
            assert lowered_key != "other_options"
            assert lowered_key != "options"
            assert_no_answer_fields(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_no_answer_fields(nested)


def test_eval_set_contains_all_gold_sets_and_valid_payloads():
    items = read_json(DATA / "processed" / "eval_set_v1.json")
    quiz = read_json(DATA / "gold" / "quiz_gold_v1.0.json")
    organic = read_json(DATA / "gold" / "organic_gold_v1.0.json")
    edge = read_json(DATA / "gold" / "edge_cases_v1.0.json")
    questions = {
        question["question_id"]: question
        for question in quiz["questions"]
    }
    schema = read_json(ROOT / "schemas" / "extraction_input.schema.json")
    validator = Draft7Validator(schema)
    by_set = {
        gold_set: [item for item in items if item["gold_set"] == gold_set]
        for gold_set in ("quiz", "organic", "edge")
    }

    assert len(by_set["quiz"]) == 125
    assert len(by_set["organic"]) == 20
    assert len(by_set["edge"]) == len(edge["records"])

    for item in items:
        assert item["payload"]["user_id"] == "EVAL_USER"
        assert item["payload"]["decision_id"] == item["item_id"]
        assert not list(validator.iter_errors(item["payload"]))
        assert_no_answer_fields(item["payload"])

    source_quiz = {record["record_id"]: record for record in quiz["records"]}
    eval_quiz = {item["item_id"]: item for item in by_set["quiz"]}
    assert eval_quiz.keys() == source_quiz.keys()
    for record_id, record in source_quiz.items():
        item = eval_quiz[record_id]
        assert item["payload"] == build_quiz_payload(
            scenario=record["scenario"],
            answer_text=record["answer_text"],
            question_id=record["question_id"],
            decision_id=record["record_id"],
            user_id="EVAL_USER",
        )
        assert item["gold"]["target_trait"] == record["trait_id"]
        assert item["gold"]["traits"] == {
            trait_id: (
                {"value": record["gold_value"], "confidence": record["confidence"]}
                if trait_id == record["trait_id"]
                else None
            )
            for trait_id in TRAIT_IDS
        }
        assert item["gold"]["traits"][record["trait_id"]]["value"] == record["gold_value"]
        for option in questions[record["question_id"]]["options"]:
            if option["answer"] != record["answer"]:
                assert option["text"] not in item["payload"]["decision_text"]

    organic_items = {item["item_id"]: item for item in by_set["organic"]}
    for record in organic["records"]:
        assert organic_items[record["record_id"]]["gold"]["traits"] == record["gold_traits"]

    edge_items = {item["item_id"]: item for item in by_set["edge"]}
    for record in edge["records"]:
        assert edge_items[record["record_id"]]["gold"]["expected"] == record["expected"]


def test_eval_set_and_manifest_are_deterministic_and_current():
    generated = build_eval_set()
    persisted = read_json(DATA / "processed" / "eval_set_v1.json")
    manifest = read_json(DATA / "processed" / "MANIFEST.json")
    eval_path = DATA / "processed" / "eval_set_v1.json"

    assert generated == persisted
    for relative_path, expected_hash in manifest["files"].items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash
