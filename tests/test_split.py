import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected_split():
    quiz_records = read_json(DATA / "gold" / "quiz_gold_v1.0.json")["records"]
    organic_records = read_json(DATA / "gold" / "organic_gold_v1.0.json")["records"]

    quiz_questions_by_trait = {}
    question_by_record = {}
    for record in quiz_records:
        quiz_questions_by_trait.setdefault(record["trait_id"], set()).add(
            record["question_id"]
        )
        question_by_record[record["record_id"]] = record["question_id"]

    quiz_rng = random.Random(42)
    heldout_questions = set()
    for trait_id in sorted(quiz_questions_by_trait):
        heldout_questions.update(
            quiz_rng.sample(sorted(quiz_questions_by_trait[trait_id]), 2)
        )
    quiz_heldout = [
        record["record_id"]
        for record in quiz_records
        if record["question_id"] in heldout_questions
    ]
    quiz_dev = [
        record["record_id"]
        for record in quiz_records
        if record["question_id"] not in heldout_questions
    ]

    organic_rng = random.Random(42)
    edge_case_records = sorted(
        record["record_id"]
        for record in organic_records
        if record["edge_case"] is not None
    )
    ordinary_records = sorted(
        record["record_id"]
        for record in organic_records
        if record["edge_case"] is None
    )
    organic_heldout_ids = set(organic_rng.sample(edge_case_records, 2))
    organic_heldout_ids.update(organic_rng.sample(ordinary_records, 4))
    organic_heldout = [
        record["record_id"]
        for record in organic_records
        if record["record_id"] in organic_heldout_ids
    ]
    organic_dev = [
        record["record_id"]
        for record in organic_records
        if record["record_id"] not in organic_heldout_ids
    ]
    return {
        "quiz": {"dev": quiz_dev, "heldout": quiz_heldout},
        "organic": {"dev": organic_dev, "heldout": organic_heldout},
        "edge": {
            "dev": [
                record["record_id"]
                for record in read_json(DATA / "gold" / "edge_cases_v1.0.json")["records"]
            ],
            "heldout": [],
        },
        "question_by_record": question_by_record,
        "heldout_questions": heldout_questions,
    }


def test_split_is_deterministic_for_seed_42():
    split = read_json(DATA / "processed" / "split_v1.json")
    expected = expected_split()

    assert split["header"]["seed"] == 42
    assert split["quiz"] == expected["quiz"]
    assert split["organic"] == expected["organic"]
    assert split["edge"] == expected["edge"]


def test_quiz_questions_are_never_split_and_counts_are_stratified():
    split = read_json(DATA / "processed" / "split_v1.json")
    expected = expected_split()
    quiz_records = read_json(DATA / "gold" / "quiz_gold_v1.0.json")["records"]
    dev_questions = {
        expected["question_by_record"][record_id]
        for record_id in split["quiz"]["dev"]
    }
    heldout_questions = {
        expected["question_by_record"][record_id]
        for record_id in split["quiz"]["heldout"]
    }

    assert len(split["quiz"]["dev"]) == 75
    assert len(split["quiz"]["heldout"]) == 50
    assert dev_questions.isdisjoint(heldout_questions)
    assert len(heldout_questions) == 10
    for trait_id in {record["trait_id"] for record in quiz_records}:
        trait_questions = {
            record["question_id"]
            for record in quiz_records
            if record["trait_id"] == trait_id
        }
        assert len(trait_questions.intersection(heldout_questions)) == 2
    for question_id in heldout_questions:
        assert sum(
            record["question_id"] == question_id
            for record in quiz_records
            if record["record_id"] in split["quiz"]["heldout"]
        ) == 5


def test_organic_split_has_six_holdout_items_including_two_edge_cases():
    split = read_json(DATA / "processed" / "split_v1.json")
    records = read_json(DATA / "gold" / "organic_gold_v1.0.json")["records"]
    records_by_id = {record["record_id"]: record for record in records}

    assert len(split["organic"]["dev"]) == 14
    assert len(split["organic"]["heldout"]) == 6
    assert sum(
        records_by_id[record_id]["edge_case"] is not None
        for record_id in split["organic"]["heldout"]
    ) >= 2
    assert split["edge"]["heldout"] == []
    assert len(split["edge"]["dev"]) == len(
        read_json(DATA / "gold" / "edge_cases_v1.0.json")["records"]
    )
