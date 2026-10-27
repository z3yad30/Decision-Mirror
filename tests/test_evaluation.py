from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from decision_mirror.extraction import validation
from evaluation.metrics import analyze_items, is_grounded, score_band
from evaluation.runner import evaluate_run

ROOT = Path(__file__).resolve().parents[1]
_COMPARE_SPEC = importlib.util.spec_from_file_location(
    "compare_runs", ROOT / "scripts" / "compare_runs.py"
)
assert _COMPARE_SPEC is not None and _COMPARE_SPEC.loader is not None
compare_runs = importlib.util.module_from_spec(_COMPARE_SPEC)
_COMPARE_SPEC.loader.exec_module(compare_runs)
TRAITS = (
    "Risk Tolerance",
    "Time Horizon",
    "Locus of Priority",
    "Decisiveness Speed",
    "Emotional vs. Analytical Weighting",
    "Self-Consistency",
)


def _quiz_item(index: int, trait_id: str, score: float = 0.5) -> dict:
    gold_traits = {f"T{i:02d}": None for i in range(1, 7)}
    gold_traits[trait_id] = {"value": score, "confidence": 0.7}
    return {
        "item_id": f"Q{index:02d}",
        "gold_set": "quiz",
        "split": "dev",
        "payload": {
            "decision_id": f"Q{index:02d}",
            "user_id": "TEST_USER",
            "source_type": "onboarding_quiz",
            "decision_text": f"Decision evidence {index}.",
            "ontology_version": "v1.0",
            "language": "en",
            "context": {"question_id": f"Q{index:02d}"},
        },
        "gold": {
            "target_trait": trait_id,
            "traits": gold_traits,
            "situational_factor": None,
            "ambiguous_gold": False,
        },
    }


def _response(item: dict, scores: dict[str, float | None]) -> dict:
    traits = []
    for index, trait_id in enumerate((f"T{i:02d}" for i in range(1, 7))):
        score = scores.get(trait_id)
        traits.append(
            {
                "trait_id": trait_id,
                "trait_name": TRAITS[index],
                "score": score,
                "confidence": 0.7 if score is not None else 0.0,
                "evidence": (
                    [item["payload"]["decision_text"]]
                    if score is not None
                    else []
                ),
                "situational_factor": None,
                "context_notes": (
                    "Supported by the decision evidence."
                    if score is not None
                    else "Insufficient evidence in this decision."
                ),
            }
        )
    return {
        "decision_id": item["item_id"],
        "extraction_status": (
            "success"
            if any(score is not None for score in scores.values())
            else "insufficient_evidence"
        ),
        "traits": traits,
    }


def _analyze(items: list[dict], scores: list[dict[str, float | None]]) -> dict:
    rows = [
        {
            "item_id": item["item_id"],
            "response_text": json.dumps(_response(item, score)),
        }
        for item, score in zip(items, scores)
    ]
    return analyze_items(items, rows, validation)


def test_perfect_quiz_run_has_zero_mae_and_unit_weighted_kappa():
    gold = [0.1, 0.3, 0.5, 0.7, 0.9]
    items = [
        _quiz_item(index, f"T{index:02d}", score)
        for index, score in enumerate(gold, 1)
    ]
    predictions = [{f"T{index:02d}": score} for index, score in enumerate(gold, 1)]

    metrics = _analyze(items, predictions)["metrics"]["quiz"][
        "target_trait_scoring"
    ]["overall"]

    assert metrics["mae"] == 0
    assert metrics["quadratic_weighted_kappa"] == 1
    assert metrics["exact_band_accuracy"] == 1
    assert metrics["spearman_rho"] == 1


def test_inverted_t03_is_counted_as_polarity_inversion():
    item = _quiz_item(1, "T03", 0.1)
    result = _analyze([item], [{"T03": 0.9}])

    assert result["metrics"]["quiz"]["target_trait_scoring"]["T03"][
        "polarity_inversions"
    ] == 1
    assert any(
        error["error_type"] == "polarity_inversion"
        for error in result["errors"]
    )


def test_t06_violation_is_counted_even_when_semantic_validation_fails():
    item = _quiz_item(1, "T01", 0.1)
    response = _response(item, {"T01": 0.1, "T06": 0.8})
    result = analyze_items(
        [item],
        [{"item_id": item["item_id"], "response_text": json.dumps(response)}],
        validation,
    )

    assert result["metrics"]["t06_violations"]["count"] == 1
    assert any(
        error["error_type"] == "t06_violation"
        for error in result["errors"]
    )


def test_recovered_json_is_flagged_but_never_treated_as_valid():
    item = _quiz_item(1, "T01", 0.1)
    text = "Here is the result:\n" + json.dumps(_response(item, {"T01": 0.1}))
    result = analyze_items(
        [item],
        [{"item_id": item["item_id"], "response_text": text}],
        validation,
    )

    assert result["compliance"][0]["recovered"] is True
    assert result["compliance"][0]["strict_json_parse"] is False
    assert result["compliance"][0]["semantic_valid"] is False
    malformed = next(
        error for error in result["errors"]
        if error["error_type"] == "malformed_output"
    )
    assert malformed["severity"] == "critical"


def test_null_everything_reports_zero_non_null_and_missed_signal_for_all():
    items = [
        _quiz_item(index, f"T{index:02d}", 0.1 * index)
        for index in range(1, 6)
    ]
    result = _analyze(items, [{} for _ in items])

    quiz = result["metrics"]["quiz"]["target_trait_scoring"]
    assert quiz["overall"]["target_non_null_rate"] == 0
    assert sum(
        error["error_type"] == "missed_signal" for error in result["errors"]
    ) == 5


def test_half_open_score_band_boundaries():
    assert [score_band(score) for score in (0.2, 0.4, 0.6, 0.8)] == [
        1,
        2,
        3,
        4,
    ]


def test_grounding_accepts_balanced_quote_delimiters_around_excerpt():
    quote = (
        "“turned down three promotions in a row because each one would have "
        "meant more travel and less time with my kids”"
    )
    decision_text = (
        "I've turned down three promotions in a row because each one would "
        "have meant more travel and less time with my kids."
    )

    assert is_grounded(quote, decision_text)


def test_ambiguous_organic_items_are_excluded_from_headline_metrics():
    item = {
        "item_id": "ORG04",
        "gold_set": "organic",
        "split": "dev",
        "payload": {
            "decision_id": "ORG04",
            "user_id": "TEST_USER",
            "source_type": "decision_log",
            "decision_text": "I considered the risky choice.",
            "ontology_version": "v1.0",
            "language": "en",
        },
        "gold": {
            "traits": {
                "T01": {"value": None, "confidence": 0.35},
                **{f"T{i:02d}": None for i in range(2, 7)},
            },
            "situational_factor": None,
            "ambiguous_gold": True,
            "evidence": [],
        },
    }
    result = _analyze([item], [{"T01": 0.9}])
    organic = result["metrics"]["organic"]

    assert organic["score_metrics"]["overall"]["n_paired_scores"] == 0
    assert organic["ambiguous_gold_item_count"] == 1
    assert organic["ambiguous_gold_separate"][0]["item_id"] == "ORG04"
    assert not any(
        error["error_type"] == "unsupported_inference"
        for error in result["errors"]
    )


def test_evaluation_does_not_modify_raw_responses(tmp_path: Path):
    items = [_quiz_item(1, "T01", 0.1)]
    score = {"T01": 0.1}
    raw = {
        "item_id": items[0]["item_id"],
        "response_text": json.dumps(_response(items[0], score)),
    }
    runs_dir = tmp_path / "runs"
    run_dir = runs_dir / "fixture"
    run_dir.mkdir(parents=True)
    eval_path = tmp_path / "eval.json"
    eval_path.write_text(json.dumps(items), encoding="utf-8")
    raw_path = run_dir / "raw_responses.jsonl"
    raw_path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
    raw_hash_before = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    eval_hash = hashlib.sha256(eval_path.read_bytes()).hexdigest()
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "eval_set_sha256": eval_hash,
                "set": "quiz",
                "split": "dev",
                "prompt_version": "v2.0",
                "model": "synthetic",
            }
        ),
        encoding="utf-8",
    )
    organic_gold = tmp_path / "organic.json"
    organic_gold.write_text(json.dumps({"records": []}), encoding="utf-8")

    evaluate_run(
        "fixture",
        runs_dir=runs_dir,
        results_dir=tmp_path / "results",
        eval_set_path=eval_path,
        organic_gold_path=organic_gold,
    )

    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == raw_hash_before
    assert {
        "metrics.json",
        "per_item.csv",
        "error_log.jsonl",
        "schema_compliance.json",
        "tables.md",
        "difficult_cases.md",
    } <= {path.name for path in (tmp_path / "results" / "fixture").iterdir()}


def test_paired_comparison_reports_common_items_and_null_transitions():
    run_a = [
        {
            "item_id": "Q01",
            "gold_set": "quiz",
            "target_trait": "T01",
            "gold_score_T01": 0.1,
            "score_T01": None,
        },
        {
            "item_id": "Q02",
            "gold_set": "quiz",
            "target_trait": "T02",
            "gold_score_T02": 0.3,
            "score_T02": 0.3,
        },
    ]
    run_b = [
        {
            "item_id": "Q01",
            "gold_set": "quiz",
            "target_trait": "T01",
            "gold_score_T01": 0.1,
            "score_T01": 0.1,
        },
        {
            "item_id": "Q02",
            "gold_set": "quiz",
            "target_trait": "T02",
            "gold_score_T02": 0.3,
            "score_T02": 0.5,
        },
    ]

    report = compare_runs._paired_report("a", "b", run_a, run_b)

    assert report["common_item_count"] == 2
    assert report["paired_numeric_score_count"] == 1
    assert report["score_comparison_by_trait"]["T01"]["null_to_score_b_count"] == 1
    assert report["score_comparison_by_trait"]["T02"]["mae_b"] == 0.2
