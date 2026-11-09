from __future__ import annotations

import hashlib
import inspect
import json
import math
import random
import re
from pathlib import Path
from typing import Any

from decision_mirror.extraction.validation import classify_response

from evaluation.metrics import SCORED_TRAITS, is_grounded, score_band, spearman_rho
from evaluation.metrics import normalize_quote as corrected_normalize_quote


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "evaluation" / "runs"
RESULTS_DIR = ROOT / "evaluation" / "results"
EVAL_SET_PATH = ROOT / "data" / "processed" / "eval_set_v1.json"
QUIZ_GOLD_PATH = ROOT / "data" / "gold" / "quiz_gold_v1.0.json"
RUN_IDS = (
    "v2.0__openai-gpt-oss-120b__all-dev__5825600d",
    "v2.0__openai-gpt-oss-120b__all-heldout__5825600d",
    "v2.1__openai-gpt-oss-120b__all-dev__5825600d",
)
POST_HOC_LABEL = "post-hoc: added after dev and held-out results were seen"
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_SEED = 42

_ORIGINAL_NORMALIZER_SOURCE = (
    "def normalize_quote(text: str) -> str:\n"
    "    return _WHITESPACE.sub(\" \", text.translate(_QUOTE_TRANSLATION)).strip().casefold()\n"
)


_WHITESPACE = re.compile(r"\s+")
_QUOTE_TRANSLATION = str.maketrans(
    {
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u00ab": '"',
        "\u00bb": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u0060": "'",
    }
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"expected JSON object at {path}:{line_number}")
        rows.append(value)
    return rows


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _read_run(
    run_id: str,
    *,
    runs_dir: Path,
    results_dir: Path,
    eval_set_path: Path,
    quiz_gold_path: Path,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    run_dir = runs_dir / run_id
    result_dir = results_dir / run_id
    manifest = _read_json(run_dir / "manifest.json")
    raw_rows = _read_jsonl(run_dir / "raw_responses.jsonl")
    metrics_path = result_dir / "metrics.json"
    if not metrics_path.is_file():
        raise FileNotFoundError(f"existing metrics are required: {metrics_path}")
    metrics = _read_json(metrics_path)
    eval_bytes = eval_set_path.read_bytes()
    if manifest.get("eval_set_sha256") != hashlib.sha256(eval_bytes).hexdigest():
        raise ValueError(f"evaluation-set hash mismatch for {run_id}")
    items = _read_json(eval_set_path)
    selected = [
        item
        for item in items
        if (manifest.get("set", "all") == "all" or item["gold_set"] == manifest["set"])
        and (manifest.get("split", "all") == "all" or item["split"] == manifest["split"])
    ]
    selected_ids = {item["item_id"] for item in selected}
    if any(row.get("item_id") not in selected_ids for row in raw_rows):
        raise ValueError(f"run {run_id} contains responses outside its selected split")
    quiz_gold = _read_json(quiz_gold_path)
    quiz_records = {record["record_id"]: record for record in quiz_gold["records"]}
    return manifest, selected, raw_rows, metrics, quiz_records


def _quiz_off_target_analysis(
    items: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
    quiz_records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    quiz_items = [item for item in items if item["gold_set"] == "quiz"]
    raw_by_id = {row["item_id"]: row for row in raw_rows}
    unassessed_labels = []
    details = []
    review_candidates = []
    scored_count = 0

    for item in quiz_items:
        item_id = item["item_id"]
        gold_record = quiz_records[item_id]
        target_trait = item["gold"]["target_trait"]
        if gold_record["trait_id"] != target_trait:
            raise ValueError(f"quiz target-trait mismatch for {item_id}")
        if any(
            key in gold_record
            for key in ("gold_traits", "trait_scores", "traits", "labels")
        ):
            unassessed_labels.append(item_id)

        raw = raw_by_id.get(item_id)
        outcome = (
            classify_response(raw.get("response_text", ""), item["payload"])
            if raw is not None
            else None
        )
        response = outcome.response if outcome is not None and outcome.valid else None
        traits = {
            trait["trait_id"]: trait
            for trait in response.get("traits", [])
        } if response else {}
        scored_traits = []
        for trait_id in SCORED_TRAITS:
            if trait_id == target_trait:
                continue
            trait = traits.get(trait_id)
            score = trait.get("score") if trait else None
            if score is None:
                continue
            evidence = trait.get("evidence", [])
            quotes = [
                {"quote": quote, "grounded": is_grounded(quote, item["payload"]["decision_text"])}
                for quote in evidence
                if isinstance(quote, str)
            ]
            evidence_exists = bool(quotes)
            evidence_grounded = evidence_exists and all(quote["grounded"] for quote in quotes)
            scored = {
                "trait_id": trait_id,
                "score": score,
                "confidence": trait.get("confidence"),
                "evidence_quotes_exist": evidence_exists,
                "evidence_quotes_grounded": evidence_grounded,
                "evidence_quotes": quotes,
            }
            scored_traits.append(scored)
            scored_count += 1
        detail = {
            "item_id": item_id,
            "question_id": item["payload"].get("context", {}).get("question_id"),
            "target_trait": target_trait,
            "response_present": raw is not None,
            "scored_non_target_traits": scored_traits,
        }
        details.append(detail)
        if scored_traits:
            review_candidates.append(detail)

    if unassessed_labels:
        raise ValueError(
            "quiz_gold contains non-target trait-label collections for "
            + ", ".join(unassessed_labels)
        )
    possible_count = (len(SCORED_TRAITS) - 1) * sum(
        item["item_id"] in raw_by_id for item in quiz_items
    )
    return {
        "gold_verification": {
            "quiz_gold_record_count": len(quiz_records),
            "non_target_trait_label_count": 0,
            "finding": (
                "Each quiz gold record contains one target trait and one score; "
                "no non-target trait labels are supplied."
            ),
        },
        "off_target_scoring_rate": {
            "scored_non_target_trait_count": scored_count,
            "possible_non_target_trait_count": possible_count,
            "rate": scored_count / possible_count if possible_count else None,
            "interpretation": "Descriptive off-target scoring rate, not an error rate.",
        },
        "quiz_items": details,
        "human_review_candidates": review_candidates,
        "unassessed": ["quiz non-target traits", "T06"],
        "evaluated_against_gold": [
            "quiz target traits",
            "organic T01-T05, including gold-null unsupported-inference opportunities already in metrics.json",
            "edge-case behavior checks",
        ],
    }


def _situational_factor_summary(metrics: dict[str, Any]) -> dict[str, Any]:
    try:
        factor = metrics["organic"]["score_metrics"]["overall"].get(
            "situational_factor"
        )
    except KeyError as error:
        raise ValueError(
            "existing metrics.json does not report factor metrics separately"
        ) from error
    if not isinstance(factor, dict):
        raise ValueError("existing metrics.json has no situational-factor summary")
    required = ("precision", "recall", "category_agreement", "true_positive", "false_positive", "false_negative")
    missing = [key for key in required if key not in factor]
    if missing:
        raise ValueError(
            "existing metrics.json does not report factor metrics separately: "
            + ", ".join(missing)
        )
    tp, fp, fn = (
        factor["true_positive"],
        factor["false_positive"],
        factor["false_negative"],
    )
    precision_n = tp + fp
    recall_n = tp + fn
    category_n = tp
    return {
        "reported_separately_in_existing_metrics_json": True,
        "precision": {
            "value": factor["precision"],
            "true_positive": tp,
            "false_positive": fp,
            "denominator": precision_n,
        },
        "recall": {
            "value": factor["recall"],
            "true_positive": tp,
            "false_negative": fn,
            "denominator": recall_n,
        },
        "category_agreement": {
            "value": factor["category_agreement"],
            "category_matches": round((factor["category_agreement"] or 0) * category_n),
            "true_positive_denominator": category_n,
        },
        "small_n_warning": (
            "Organic split sizes and positive-factor counts are small; these rates "
            "are descriptive and should not be treated as stable estimates."
        ),
    }


def _normalize_original(text: str) -> str:
    return _WHITESPACE.sub(" ", text.translate(_QUOTE_TRANSLATION)).strip().casefold()


def _quote_normalizer_comparison(
    items: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    items_by_id = {item["item_id"]: item for item in items}
    corrected_source = inspect.getsource(corrected_normalize_quote)
    corrected_hash = hashlib.sha256(corrected_source.encode("utf-8")).hexdigest()
    original_hash = hashlib.sha256(
        _ORIGINAL_NORMALIZER_SOURCE.encode("utf-8")
    ).hexdigest()
    original_grounded = 0
    corrected_grounded = 0
    quote_count = 0
    differences = []

    for row in raw_rows:
        item = items_by_id[row["item_id"]]
        outcome = classify_response(row.get("response_text", ""), item["payload"])
        if not outcome.valid or outcome.response is None:
            continue
        text = item["payload"]["decision_text"]
        for trait in outcome.response["traits"]:
            for quote in trait["evidence"]:
                old_status = bool(
                    _normalize_original(quote)
                    and _normalize_original(quote) in _normalize_original(text)
                )
                corrected_status = is_grounded(quote, text)
                quote_count += 1
                original_grounded += old_status
                corrected_grounded += corrected_status
                if old_status != corrected_status:
                    differences.append(
                        {
                            "item_id": row["item_id"],
                            "trait_id": trait["trait_id"],
                            "quote": quote,
                            "original_grounded": old_status,
                            "corrected_grounded": corrected_status,
                        }
                    )

    return {
        "original_source": {
            "git_ref": "523adc3:evaluation/metrics.py",
            "sha256": original_hash,
        },
        "corrected_source": {
            "file": "evaluation/metrics.py",
            "sha256": corrected_hash,
            "official": True,
        },
        "quote_count": quote_count,
        "original_grounded_count": original_grounded,
        "corrected_grounded_count": corrected_grounded,
        "original_grounding_rate": original_grounded / quote_count if quote_count else None,
        "corrected_grounding_rate": corrected_grounded / quote_count if quote_count else None,
        "differing_quotes": differences,
    }


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _point_metrics(pairs: list[tuple[float, float]]) -> dict[str, float | int | None]:
    directional = [(gold, predicted) for gold, predicted in pairs if gold != 0.5]
    return {
        "n_paired_scores": len(pairs),
        "mae": _mean([abs(gold - predicted) for gold, predicted in pairs]),
        "exact_band_accuracy": _mean([
            float(score_band(gold) == score_band(predicted))
            for gold, predicted in pairs
        ]),
        "spearman_rho": spearman_rho(
            [gold for gold, _ in pairs],
            [predicted for _, predicted in pairs],
        ),
        "direction_accuracy": _mean([
            float((gold < 0.5) == (predicted < 0.5))
            for gold, predicted in directional
        ]),
        "direction_n": len(directional),
    }


def _percentile_interval(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"lower": None, "upper": None, "valid_replicates": 0}
    values.sort()
    return {
        "lower": values[max(0, math.floor(0.025 * (len(values) - 1)))],
        "upper": values[min(len(values) - 1, math.ceil(0.975 * (len(values) - 1)))],
        "valid_replicates": len(values),
    }


def _cluster_bootstrap(
    cluster_pairs: dict[str, list[tuple[float, float]]],
    *,
    seed: int,
    replicates: int,
) -> dict[str, Any]:
    cluster_ids = sorted(cluster_pairs)
    if not cluster_ids:
        return {
            "cluster_count": 0,
            "point_estimates": _point_metrics([]),
            "bootstrap_95_ci": {
                name: _percentile_interval([])
                for name in ("mae", "exact_band_accuracy", "spearman_rho", "direction_accuracy")
            },
        }

    point_pairs = [pair for cluster in cluster_ids for pair in cluster_pairs[cluster]]
    estimates: dict[str, list[float]] = {
        name: []
        for name in ("mae", "exact_band_accuracy", "spearman_rho", "direction_accuracy")
    }
    rng = random.Random(seed)
    for _ in range(replicates):
        selected = [cluster_ids[rng.randrange(len(cluster_ids))] for _ in cluster_ids]
        pairs = [pair for cluster in selected for pair in cluster_pairs[cluster]]
        point = _point_metrics(pairs)
        for name in estimates:
            value = point[name]
            if isinstance(value, (int, float)) and math.isfinite(value):
                estimates[name].append(float(value))

    return {
        "cluster_count": len(cluster_ids),
        "point_estimates": _point_metrics(point_pairs),
        "bootstrap_95_ci": {
            name: _percentile_interval(values)
            for name, values in estimates.items()
        },
    }


def _quiz_cluster_bootstrap(
    items: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
    existing_metrics: dict[str, Any],
) -> dict[str, Any]:
    quiz_items = [item for item in items if item["gold_set"] == "quiz"]
    raw_by_id = {row["item_id"]: row for row in raw_rows}
    pairs_by_trait_question: dict[str, dict[str, list[tuple[float, float]]]] = {
        trait_id: {} for trait_id in SCORED_TRAITS
    }
    all_questions = {
        item["payload"]["context"]["question_id"] for item in quiz_items
    }

    for item in quiz_items:
        row = raw_by_id.get(item["item_id"])
        if row is None:
            continue
        outcome = classify_response(row.get("response_text", ""), item["payload"])
        if not outcome.valid or outcome.response is None:
            continue
        target = item["gold"]["target_trait"]
        gold_value = item["gold"]["traits"][target]["value"]
        traits = {trait["trait_id"]: trait for trait in outcome.response["traits"]}
        predicted = traits[target]["score"]
        if gold_value is None or predicted is None:
            continue
        question_id = item["payload"]["context"]["question_id"]
        pairs_by_trait_question[target].setdefault(question_id, []).append(
            (float(gold_value), float(predicted))
        )

    overall_clusters = {question_id: [] for question_id in all_questions}
    for trait_id, question_pairs in pairs_by_trait_question.items():
        for question_id, pairs in question_pairs.items():
            overall_clusters[question_id].extend(pairs)

    report: dict[str, Any] = {}
    for trait_id in (*SCORED_TRAITS, "overall"):
        clusters = (
            overall_clusters
            if trait_id == "overall"
            else {
                question_id: pairs_by_trait_question[trait_id].get(question_id, [])
                for question_id in {
                    item["payload"]["context"]["question_id"]
                    for item in quiz_items
                    if item["gold"]["target_trait"] == trait_id
                }
            }
        )
        cluster_result = _cluster_bootstrap(
            clusters,
            seed=BOOTSTRAP_SEED,
            replicates=BOOTSTRAP_REPLICATES,
        )
        existing = existing_metrics["quiz"]["target_trait_scoring"][trait_id]
        cluster_result["existing_item_level"] = {
            "bootstrap_95_ci": existing["bootstrap_95_ci"],
            "point_estimates": {
                "mae": existing["mae"],
                "exact_band_accuracy": existing["exact_band_accuracy"],
                "spearman_rho": existing["spearman_rho"],
                "direction_accuracy": existing["direction_accuracy"],
            },
            "direction_accuracy": existing["direction_accuracy"],
            "direction_n": existing["direction_n"],
            "direction_ci": None,
        }
        report[trait_id] = cluster_result

    total_clusters = len(all_questions)
    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED,
        "cluster_definition": "One question ID, including its five answer-option records, is one resampling unit.",
        "cluster_count": total_clusters,
        "expected_cluster_count_check": {
            "actual": total_clusters,
            "expected": 15 if total_clusters == 15 else 10 if total_clusters == 10 else None,
            "matches_expected_dev_or_heldout_count": total_clusters in {10, 15},
        },
        "metrics": report,
        "stability_warning": (
            f"{total_clusters} question clusters overall (and only "
            f"{min((result['cluster_count'] for result in report.values() if result['cluster_count']), default=0)} "
            "clusters for an individual trait) is too small to support stable intervals."
        ),
        "thresholds": _threshold_information(existing_metrics, report["overall"]),
    }


def _threshold_information(
    metrics: dict[str, Any], overall_cluster: dict[str, Any]
) -> dict[str, Any]:
    criterion_map = {
        "mae": ("quiz_mae", "mae"),
        "exact_band_accuracy": ("quiz_exact_band_accuracy", "exact_band_accuracy"),
        "spearman_rho": ("quiz_spearman_rho", "spearman_rho"),
        "direction_accuracy": ("quiz_direction_accuracy", "direction_accuracy"),
    }
    result = {}
    for metric, (criterion, ci_metric) in criterion_map.items():
        criterion_data = metrics["readiness_criteria"][criterion]
        interval = overall_cluster["bootstrap_95_ci"][ci_metric]
        lower = interval["lower"]
        upper = interval["upper"]
        threshold = criterion_data["threshold"]
        operator = criterion_data["operator"]
        lower_meets = (
            lower >= threshold if operator == "at_least"
            else lower <= threshold if lower is not None
            else None
        )
        appropriate_bound = upper if operator == "at_most" else lower
        appropriate_meets = (
            appropriate_bound <= threshold
            if operator == "at_most" and appropriate_bound is not None
            else appropriate_bound >= threshold
            if appropriate_bound is not None
            else None
        )
        result[metric] = {
            "operator": operator,
            "threshold": threshold,
            "lower_bound": lower,
            "lower_bound_meets_threshold": lower_meets,
            "appropriate_ci_bound": "upper" if operator == "at_most" else "lower",
            "appropriate_bound_meets_threshold": appropriate_meets,
            "information_only": True,
        }
    return result


def _format_rate(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def _format_interval(interval: dict[str, Any]) -> str:
    lower, upper = interval["lower"], interval["upper"]
    if lower is None or upper is None:
        return "n/a"
    return f"[{lower:.3f}, {upper:.3f}]"


def _format_estimate(
    estimate: float | None, interval: dict[str, Any]
) -> str:
    if estimate is None:
        return "n/a"
    return f"{estimate:.3f} {_format_interval(interval)}"


def _render_supplementary(report: dict[str, Any]) -> str:
    run_id = report["run_id"]
    off_target = report["non_target_traits"]
    factor = report["situational_factors"]
    quote = report["quote_normalizer_comparison"]
    bootstrap = report["quiz_question_cluster_bootstrap"]
    lines = [
        f"# Post-hoc supplementary analyses — {run_id}",
        "",
        f"**{POST_HOC_LABEL}.** These analyses are supplementary and do not alter `metrics.json`, `tables.md`, or report headline values.",
        "",
        "## Quiz non-target traits",
        "",
        off_target["gold_verification"]["finding"],
        "Off-target scoring is descriptive, not an error rate. Quiz non-target traits and T06 are unassessed against gold.",
        "",
        f"Off-target scoring: {off_target['off_target_scoring_rate']['scored_non_target_trait_count']}/"
        f"{off_target['off_target_scoring_rate']['possible_non_target_trait_count']} "
        f"({ _format_rate(off_target['off_target_scoring_rate']['rate']) }).",
        "",
        "| Quiz item | Target trait | Non-target scored traits (score; confidence; evidence quotes; grounded) |",
        "|---|---|---|",
    ]
    for item in off_target["quiz_items"]:
        scored = item["scored_non_target_traits"]
        summary = "; ".join(
            f"{entry['trait_id']}={entry['score']:.3f}; "
            f"confidence={entry['confidence']}; "
            f"quotes={'yes' if entry['evidence_quotes_exist'] else 'no'}; "
            f"grounded={'yes' if entry['evidence_quotes_grounded'] else 'no'}"
            for entry in scored
        ) or "none"
        lines.append(f"| {item['item_id']} | {item['target_trait']} | {summary} |")
    lines.extend(["", "Off-target cases for human review (no decisions made):"])
    candidates = off_target["human_review_candidates"]
    lines.extend(
        f"- `{item['item_id']}`: "
        + ", ".join(trait["trait_id"] for trait in item["scored_non_target_traits"])
        for item in candidates
    )
    if not candidates:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Situational factors",
            "",
            "Precision, recall, and category agreement are each already reported separately in the existing `metrics.json`; values below preserve those numbers and expose denominators.",
            "",
            f"- Precision: {factor['precision']['true_positive']}/{factor['precision']['denominator']} = {_format_rate(factor['precision']['value'])} (TP/TP+FP).",
            f"- Recall: {factor['recall']['true_positive']}/{factor['recall']['denominator']} = {_format_rate(factor['recall']['value'])} (TP/TP+FN).",
            f"- Category agreement: {factor['category_agreement']['category_matches']}/{factor['category_agreement']['true_positive_denominator']} = {_format_rate(factor['category_agreement']['value'])} among true positives.",
            "",
            f"**Small-n warning:** {factor['small_n_warning']}",
            "",
            "## Quote-normalizer comparison",
            "",
            f"Original normalizer recovered from Git (`{quote['original_source']['git_ref']}`), SHA-256 `{quote['original_source']['sha256']}`; corrected official normalizer SHA-256 `{quote['corrected_source']['sha256']}`.",
            f"Grounded quotes: original {quote['original_grounded_count']}/{quote['quote_count']} ({_format_rate(quote['original_grounding_rate'])}); corrected {quote['corrected_grounded_count']}/{quote['quote_count']} ({_format_rate(quote['corrected_grounding_rate'])}).",
            "",
            "| Item | Trait | Quote | Original | Corrected |",
            "|---|---|---|---|---|",
        ]
    )
    for difference in quote["differing_quotes"]:
        safe_quote = difference["quote"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {difference['item_id']} | {difference['trait_id']} | "
            f"`{safe_quote}` | {difference['original_grounded']} | "
            f"{difference['corrected_grounded']} |"
        )
    if not quote["differing_quotes"]:
        lines.append("| None | — | No quote status changed. | — | — |")

    lines.extend(
        [
            "",
            "## Quiz question-level cluster bootstrap",
            "",
            f"Resampling unit: one quiz question with its five answer options. {bootstrap['replicates']} replicates; seed {bootstrap['seed']}; {bootstrap['cluster_count']} overall question clusters.",
            f"**Stability limitation:** {bootstrap['stability_warning']}",
            "",
            "| Trait | Clusters | MAE item point [CI] | MAE cluster point [CI] | Exact-band item point [CI] | Exact-band cluster point [CI] | Spearman item point [CI] | Spearman cluster point [CI] | Direction item point (no CI stored) | Direction cluster point [CI] |",
            "|---|---:|---|---|---|---|---:|---|---:|---|",
        ]
    )
    for trait_id, result in bootstrap["metrics"].items():
        item_ci = result["existing_item_level"]["bootstrap_95_ci"]
        cluster_ci = result["bootstrap_95_ci"]
        lines.append(
            f"| {trait_id} | {result['cluster_count']} | "
            f"{_format_estimate(result['existing_item_level']['point_estimates']['mae'], item_ci['mae'])} | "
            f"{_format_estimate(result['point_estimates']['mae'], cluster_ci['mae'])} | "
            f"{_format_estimate(result['existing_item_level']['point_estimates']['exact_band_accuracy'], item_ci['accuracy'])} | "
            f"{_format_estimate(result['point_estimates']['exact_band_accuracy'], cluster_ci['exact_band_accuracy'])} | "
            f"{_format_estimate(result['existing_item_level']['point_estimates']['spearman_rho'], item_ci['rho'])} | "
            f"{_format_estimate(result['point_estimates']['spearman_rho'], cluster_ci['spearman_rho'])} | "
            f"{_format_rate(result['existing_item_level']['direction_accuracy'])} | "
            f"{_format_estimate(result['point_estimates']['direction_accuracy'], cluster_ci['direction_accuracy'])} |"
        )
    lines.extend(
        [
            "",
            "Direction has no stored item-level confidence interval; only its existing point estimate is shown. Threshold comparisons below are information only; no pre-registered threshold was changed.",
            "",
            "| Metric | Preregistered threshold | Cluster lower bound | Lower bound alone meets threshold | Relevant bound meets threshold |",
            "|---|---|---:|---|---|",
        ]
    )
    for metric, values in bootstrap["thresholds"].items():
        lower = values["lower_bound"]
        rendered_lower = "n/a" if lower is None else f"{lower:.3f}"
        lines.append(
            f"| {metric} | {values['operator']} {values['threshold']:.3f} | "
            f"{rendered_lower} | {values['lower_bound_meets_threshold']} | "
            f"{values['appropriate_bound_meets_threshold']} "
            f"({values['appropriate_ci_bound']} bound) |"
        )
    lines.extend(
        [
            "",
            "For quiz gold, the evaluated trait set is the target trait only. Organic T01–T05, including gold-null unsupported-inference opportunities, and edge-case behavior are evaluated against their respective reference sets in the existing metrics. Quiz non-target traits and T06 are unassessed against gold.",
            "",
        ]
    )
    return "\n".join(lines)


def evaluate_supplementary(
    run_id: str,
    *,
    runs_dir: Path = RUNS_DIR,
    results_dir: Path = RESULTS_DIR,
    eval_set_path: Path = EVAL_SET_PATH,
    quiz_gold_path: Path = QUIZ_GOLD_PATH,
) -> dict[str, Any]:
    manifest, items, raw_rows, existing_metrics, quiz_records = _read_run(
        run_id,
        runs_dir=runs_dir,
        results_dir=results_dir,
        eval_set_path=eval_set_path,
        quiz_gold_path=quiz_gold_path,
    )
    report = {
        "label": POST_HOC_LABEL,
        "run_id": run_id,
        "split": manifest.get("split"),
        "non_target_traits": _quiz_off_target_analysis(items, raw_rows, quiz_records),
        "situational_factors": _situational_factor_summary(existing_metrics),
        "quote_normalizer_comparison": _quote_normalizer_comparison(
            items, raw_rows
        ),
        "quiz_question_cluster_bootstrap": _quiz_cluster_bootstrap(
            items, raw_rows, existing_metrics
        ),
        "evaluation_scope": {
            "evaluated_against_gold": [
                "quiz target trait",
                "organic T01-T05, including gold-null unsupported-inference opportunities already present in metrics.json",
                "edge-case behavior checks",
            ],
            "unassessed": ["quiz non-target traits", "T06"],
        },
    }
    result_dir = results_dir / run_id
    result_dir.mkdir(parents=True, exist_ok=True)
    _write_json(result_dir / "supplementary_metrics.json", report)
    (result_dir / "supplementary.md").write_text(
        _render_supplementary(report), encoding="utf-8", newline="\n"
    )
    return report
