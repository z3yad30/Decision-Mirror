from __future__ import annotations

import hashlib
import json

import pytest

from evaluation import supplementary
from evaluation.metrics import is_grounded


def test_situational_factor_summary_preserves_existing_values_and_denominators():
    metrics = {
        "organic": {
            "score_metrics": {
                "overall": {
                    "situational_factor": {
                        "precision": 0.6,
                        "recall": 1.0,
                        "category_agreement": 0.0,
                        "true_positive": 3,
                        "false_positive": 2,
                        "false_negative": 0,
                    }
                }
            }
        }
    }

    summary = supplementary._situational_factor_summary(metrics)

    assert summary["reported_separately_in_existing_metrics_json"]
    assert summary["precision"]["denominator"] == 5
    assert summary["recall"]["denominator"] == 3
    assert summary["category_agreement"]["true_positive_denominator"] == 3
    assert summary["category_agreement"]["value"] == 0.0
    with pytest.raises(ValueError, match="does not report factor metrics separately"):
        supplementary._situational_factor_summary({"organic": {"score_metrics": {}}})


def test_cluster_bootstrap_is_reproducible_and_resamples_whole_groups():
    clusters = {
        "question-a": [(0.1, 0.2), (0.3, 0.4)],
        "question-b": [(0.7, 0.8), (0.9, 0.8)],
    }

    first = supplementary._cluster_bootstrap(
        clusters, seed=42, replicates=100
    )
    second = supplementary._cluster_bootstrap(
        clusters, seed=42, replicates=100
    )

    assert first == second
    assert first["cluster_count"] == 2
    assert first["bootstrap_95_ci"]["mae"]["valid_replicates"] == 100
    assert first["bootstrap_95_ci"]["direction_accuracy"]["valid_replicates"] == 100


def test_original_quote_normalizer_is_the_pre_correction_behavior():
    quote = '"a grounded excerpt"'
    text = "a grounded excerpt"

    assert not supplementary._normalize_original(quote) in supplementary._normalize_original(text)
    assert is_grounded(quote, text)
    assert len(supplementary._ORIGINAL_NORMALIZER_SOURCE) > 0


@pytest.mark.parametrize(
    "run_id,expected_clusters,expected_possible_count",
    [
        ("v2.0__openai-gpt-oss-120b__all-dev__5825600d", 15, 300),
        ("v2.0__openai-gpt-oss-120b__all-heldout__5825600d", 10, 200),
        ("v2.1__openai-gpt-oss-120b__all-dev__5825600d", 15, 300),
    ],
)
def test_supplementary_report_writes_only_new_outputs_and_is_post_hoc(
    run_id, expected_clusters, expected_possible_count
):
    results_dir = supplementary.RESULTS_DIR / run_id
    protected = ("metrics.json", "tables.md")
    before = {
        name: hashlib.sha256((results_dir / name).read_bytes()).hexdigest()
        for name in protected
    }

    report = supplementary.evaluate_supplementary(run_id)

    after = {
        name: hashlib.sha256((results_dir / name).read_bytes()).hexdigest()
        for name in protected
    }
    assert before == after
    assert report["label"] == supplementary.POST_HOC_LABEL
    assert report["quiz_question_cluster_bootstrap"]["cluster_count"] == expected_clusters
    assert report["non_target_traits"]["gold_verification"]["non_target_trait_label_count"] == 0
    assert (
        report["non_target_traits"]["off_target_scoring_rate"][
            "possible_non_target_trait_count"
        ]
        == expected_possible_count
    )
    assert report["situational_factors"]["reported_separately_in_existing_metrics_json"]
    assert (results_dir / "supplementary_metrics.json").is_file()
    markdown = (results_dir / "supplementary.md").read_text(encoding="utf-8")
    assert supplementary.POST_HOC_LABEL in markdown
    persisted = json.loads(
        (results_dir / "supplementary_metrics.json").read_text(encoding="utf-8")
    )
    assert persisted == report
