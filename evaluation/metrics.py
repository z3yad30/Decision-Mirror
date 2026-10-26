from __future__ import annotations

import math
import random
import re
from collections import Counter
from typing import Any, Iterable

TRAIT_IDS = tuple(f"T{index:02d}" for index in range(1, 7))
SCORED_TRAITS = TRAIT_IDS[:5]
BANDS = ("[0.0,0.2)", "[0.2,0.4)", "[0.4,0.6)", "[0.6,0.8)", "[0.8,1.0]")
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "review": 3}
_WHITESPACE = re.compile(r"\s+")
_TOKEN = re.compile(r"\b[\w']+\b", re.UNICODE)
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


def score_band(score: float) -> int:
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"score outside [0, 1]: {score}")
    return min(int(score * 5), 4)


def normalize_quote(text: str) -> str:
    return _WHITESPACE.sub(" ", text.translate(_QUOTE_TRANSLATION)).strip().casefold()


def is_grounded(quote: str, decision_text: str) -> bool:
    normalized = normalize_quote(quote)
    return bool(normalized) and normalized in normalize_quote(decision_text)


def _mean(values: Iterable[float]) -> float | None:
    data = list(values)
    return sum(data) / len(data) if data else None


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        average_rank = (start + 1 + end) / 2
        for index in order[start:end]:
            ranks[index] = average_rank
        start = end
    return ranks


def _pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    left_delta = [value - left_mean for value in left]
    right_delta = [value - right_mean for value in right]
    left_ss = sum(value * value for value in left_delta)
    right_ss = sum(value * value for value in right_delta)
    if left_ss == 0 or right_ss == 0:
        return None
    return sum(a * b for a, b in zip(left_delta, right_delta)) / math.sqrt(
        left_ss * right_ss
    )


def spearman_rho(gold: list[float], predicted: list[float]) -> float | None:
    if len(gold) != len(predicted) or len(gold) < 2:
        return None
    return _pearson(_rank(gold), _rank(predicted))


def quadratic_weighted_kappa(
    gold_bands: list[int], predicted_bands: list[int]
) -> float | None:
    if len(gold_bands) != len(predicted_bands) or not gold_bands:
        return None
    observed = [[0] * 5 for _ in range(5)]
    actual_histogram = [0] * 5
    predicted_histogram = [0] * 5
    for actual, predicted in zip(gold_bands, predicted_bands):
        observed[actual][predicted] += 1
        actual_histogram[actual] += 1
        predicted_histogram[predicted] += 1
    total = len(gold_bands)
    observed_disagreement = sum(
        ((actual - predicted) ** 2 / 16) * observed[actual][predicted]
        for actual in range(5)
        for predicted in range(5)
    )
    expected_disagreement = sum(
        ((actual - predicted) ** 2 / 16)
        * actual_histogram[actual]
        * predicted_histogram[predicted]
        / total
        for actual in range(5)
        for predicted in range(5)
    )
    if expected_disagreement == 0:
        return 1.0 if observed_disagreement == 0 else None
    return 1.0 - observed_disagreement / expected_disagreement


def _bootstrap_ci(
    values: list[tuple[float, float]],
    statistic: str,
    *,
    seed: int = 42,
    replicates: int = 2000,
) -> dict[str, float | int | None]:
    if not values:
        return {"lower": None, "upper": None, "n": 0}
    rng = random.Random(seed)
    estimates: list[float] = []
    for _ in range(replicates):
        sample = [values[rng.randrange(len(values))] for _ in values]
        gold = [pair[0] for pair in sample]
        predicted = [pair[1] for pair in sample]
        if statistic == "mae":
            estimate = _mean(abs(a - b) for a, b in sample)
        elif statistic == "accuracy":
            estimate = _mean(
                float(score_band(a) == score_band(b)) for a, b in sample
            )
        else:
            estimate = spearman_rho(gold, predicted)
        if estimate is not None and math.isfinite(estimate):
            estimates.append(estimate)
    if not estimates:
        return {"lower": None, "upper": None, "n": 0}
    estimates.sort()
    lower_index = max(0, math.floor(0.025 * (len(estimates) - 1)))
    upper_index = min(len(estimates) - 1, math.ceil(0.975 * (len(estimates) - 1)))
    return {
        "lower": estimates[lower_index],
        "upper": estimates[upper_index],
        "n": len(values),
    }


def score_metrics(
    pairs: list[tuple[float, float]], *, bootstrap: bool = True
) -> dict[str, Any]:
    gold = [pair[0] for pair in pairs]
    predicted = [pair[1] for pair in pairs]
    gold_bands = [score_band(value) for value in gold]
    predicted_bands = [score_band(value) for value in predicted]
    band_differences = [
        abs(actual - model)
        for actual, model in zip(gold_bands, predicted_bands)
    ]
    directional = [
        (actual, model)
        for actual, model in pairs
        if actual != 0.5
    ]
    directional_correct = [
        (actual < 0.5) == (model < 0.5)
        for actual, model in directional
    ]
    inversions = [
        (actual, model)
        for actual, model in pairs
        if ((actual < 0.5) != (model < 0.5)) and abs(actual - model) > 0.2
    ]
    result: dict[str, Any] = {
        "n_paired_scores": len(pairs),
        "mae": _mean(abs(actual - model) for actual, model in pairs),
        "exact_band_accuracy": _mean(
            float(actual == model)
            for actual, model in zip(gold_bands, predicted_bands)
        ),
        "within_one_band_rate": _mean(
            float(difference <= 1) for difference in band_differences
        ),
        "quadratic_weighted_kappa": quadratic_weighted_kappa(
            gold_bands, predicted_bands
        ),
        "spearman_rho": spearman_rho(gold, predicted),
        "direction_accuracy": _mean(float(value) for value in directional_correct),
        "direction_n": len(directional),
        "polarity_inversions": len(inversions),
        "polarity_inversion_rate": (
            len(inversions) / len(pairs) if pairs else None
        ),
        "confusion_matrix_5x5": [
            [
                sum(
                    actual_band == row and predicted_band == column
                    for actual_band, predicted_band in zip(
                        gold_bands, predicted_bands
                    )
                )
                for column in range(5)
            ]
            for row in range(5)
        ],
    }
    if bootstrap:
        result["bootstrap_95_ci"] = {
            name: _bootstrap_ci(pairs, name)
            for name in ("mae", "accuracy", "rho")
        }
    return result


def _divide(numerator: int | float, denominator: int | float) -> float | None:
    return numerator / denominator if denominator else None


def _traits_by_id(response: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not response or not isinstance(response.get("traits"), list):
        return {}
    return {
        trait["trait_id"]: trait
        for trait in response["traits"]
        if isinstance(trait, dict) and isinstance(trait.get("trait_id"), str)
    }


def _gold_score(gold: Any) -> tuple[float | None, float | None]:
    if not isinstance(gold, dict) or not isinstance(gold.get("value"), (int, float)):
        return None, None
    confidence = gold.get("confidence")
    return float(gold["value"]), (
        float(confidence) if isinstance(confidence, (int, float)) else None
    )


def _gold_traits(item: dict[str, Any]) -> dict[str, Any]:
    gold = item.get("gold", {})
    if item.get("gold_set") == "quiz":
        return gold.get("traits", {})
    return gold.get("traits", {})


def _factor_categories(traits: dict[str, dict[str, Any]]) -> list[str]:
    return [
        trait["situational_factor"]["category"]
        for trait in traits.values()
        if isinstance(trait.get("situational_factor"), dict)
        and isinstance(trait["situational_factor"].get("category"), str)
    ]


def _expected_status(gold_traits: dict[str, Any]) -> str:
    for value in gold_traits.values():
        score, _ = _gold_score(value)
        if score is not None:
            return "success"
    return "insufficient_evidence"


def _trait_score(traits: dict[str, dict[str, Any]], trait_id: str) -> float | None:
    score = traits.get(trait_id, {}).get("score")
    return float(score) if isinstance(score, (int, float)) else None


def _trait_confidence(traits: dict[str, dict[str, Any]], trait_id: str) -> float | None:
    confidence = traits.get(trait_id, {}).get("confidence")
    return float(confidence) if isinstance(confidence, (int, float)) else None


def _token_f1(predicted: list[str], gold: list[str]) -> float | None:
    predicted_tokens = Counter(
        token for phrase in predicted for token in _TOKEN.findall(phrase.casefold())
    )
    gold_tokens = Counter(
        token for phrase in gold for token in _TOKEN.findall(phrase.casefold())
    )
    if not predicted_tokens and not gold_tokens:
        return 1.0
    overlap = sum((predicted_tokens & gold_tokens).values())
    precision = _divide(overlap, sum(predicted_tokens.values()))
    recall = _divide(overlap, sum(gold_tokens.values()))
    if precision is None or recall is None or precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _expected_edge_checks(
    expected: dict[str, Any],
    response: dict[str, Any] | None,
    predicted_traits: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    if "expect_status" in expected:
        checks["status"] = bool(
            response and response.get("extraction_status") == expected["expect_status"]
        )
    if "expect_null_traits" in expected:
        checks["null_traits"] = all(
            _trait_score(predicted_traits, trait_id) is None
            for trait_id in expected["expect_null_traits"]
        )
    if "expect_non_null_traits" in expected:
        checks["non_null_traits"] = all(
            _trait_score(predicted_traits, trait_id) is not None
            for trait_id in expected["expect_non_null_traits"]
        )
    if "expect_situational_factor" in expected:
        checks["situational_factor"] = bool(
            _factor_categories(predicted_traits)
        ) == bool(expected["expect_situational_factor"])
    if "max_confidence" in expected:
        confidences = [
            _trait_confidence(predicted_traits, trait_id)
            for trait_id in expected.get("expect_non_null_traits", [])
        ]
        checks["max_confidence"] = all(
            confidence is not None
            and confidence <= expected["max_confidence"]
            for confidence in confidences
        )
    return checks


def analyze_items(
    items: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
    validator: Any,
) -> dict[str, Any]:
    item_by_id = {item["item_id"]: item for item in items}
    raw_by_id: dict[str, dict[str, Any]] = {}
    for row in raw_rows:
        item_id = row.get("item_id")
        if item_id not in item_by_id:
            raise ValueError(f"raw response item_id is not in eval set: {item_id}")
        if item_id in raw_by_id:
            raise ValueError(f"duplicate raw response for item_id: {item_id}")
        raw_by_id[item_id] = row

    validations: dict[str, Any] = {}
    parsed_responses: dict[str, dict[str, Any] | None] = {}
    diagnostic_responses: dict[str, dict[str, Any] | None] = {}
    compliance: list[dict[str, Any]] = []
    for item in items:
        item_id = item["item_id"]
        row = raw_by_id.get(item_id)
        if row is None:
            continue
        outcome = validator.classify_response(
            row.get("response_text", ""), item["payload"]
        )
        validations[item_id] = outcome
        parsed_responses[item_id] = outcome.response
        try:
            raw_response = validator._strict_json_loads(
                row.get("response_text", "")
            )
        except (ValueError, TypeError):
            raw_response = None
        diagnostic_responses[item_id] = (
            raw_response if isinstance(raw_response, dict) else None
        )
        compliance.append(
            {
                "item_id": item_id,
                "strict_json_parse": outcome.failure_type
                not in {"empty_response", "not_json"},
                "schema_valid": not outcome.schema_errors
                and outcome.failure_type not in {"empty_response", "not_json"},
                "semantic_valid": outcome.valid,
                "recovered": outcome.recovered,
                "failure_type": outcome.failure_type,
                "schema_errors": outcome.schema_errors,
                "semantic_errors": outcome.semantic_errors,
                "warnings": outcome.warnings,
            }
        )

    scored_predictions: dict[str, dict[str, float | None]] = {}
    quiz_pairs: dict[str, list[tuple[float, float]]] = {
        trait_id: [] for trait_id in SCORED_TRAITS
    }
    quiz_non_null: dict[str, list[bool]] = {
        trait_id: [] for trait_id in SCORED_TRAITS
    }
    quiz_off_target: list[tuple[str, str, float, bool]] = []
    organic_pairs: dict[str, list[tuple[float, float]]] = {
        trait_id: [] for trait_id in SCORED_TRAITS
    }
    organic_ambiguous_pairs: dict[str, list[tuple[float, float]]] = {
        trait_id: [] for trait_id in SCORED_TRAITS
    }
    organic_missed: list[tuple[str, str]] = []
    organic_unsupported: list[tuple[str, str]] = []
    organic_confidence_errors: list[float] = []
    organic_factor_counts = Counter()
    organic_factor_category: list[bool] = []
    organic_status: list[bool] = []
    evidence_grounded_total = 0
    evidence_quote_total = 0
    organic_evidence_f1: list[float] = []
    confidence_values: list[float] = []
    confidence_correct: list[float] = []
    confidence_wrong: list[float] = []
    high_confidence_wrong: list[tuple[str, str]] = []
    t06_violations: list[str] = []
    edge_checks: list[tuple[str, dict[str, bool]]] = []
    item_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    ambiguous_scores: list[dict[str, Any]] = []
    score_correct_item_ids: list[str] = []

    for item in items:
        item_id = item["item_id"]
        raw = raw_by_id.get(item_id)
        if raw is None:
            continue
        outcome = validations[item_id]
        response = parsed_responses[item_id]
        predicted_traits = _traits_by_id(response)
        scores = {
            trait_id: _trait_score(predicted_traits, trait_id)
            for trait_id in TRAIT_IDS
        }
        scored_predictions[item_id] = scores
        gold_traits = _gold_traits(item)
        gold_set = item["gold_set"]
        decision_text = item["payload"].get("decision_text", "")
        factors = _factor_categories(predicted_traits)
        row_errors: list[str] = []

        if outcome.failure_type:
            error_type = (
                "malformed_output"
                if outcome.failure_type
                in {
                    "empty_response",
                    "not_json",
                    "schema_violation",
                    "semantic_violation",
                }
                else outcome.failure_type
            )
            errors.append(
                {
                    "item_id": item_id,
                    "expected": "strictly valid output",
                    "actual": outcome.failure_type,
                    "error_type": error_type,
                    "severity": "critical"
                    if error_type == "malformed_output"
                    else "major",
                    "notes": "; ".join(
                        outcome.schema_errors + outcome.semantic_errors
                    )
                    or outcome.failure_type,
                }
            )
            row_errors.append(error_type)

        for trait_id, predicted_trait in predicted_traits.items():
            if _trait_score(predicted_traits, trait_id) is not None:
                confidence = _trait_confidence(predicted_traits, trait_id)
                if confidence is not None:
                    confidence_values.append(confidence)
            evidence = predicted_trait.get("evidence", [])
            if isinstance(evidence, list):
                for quote in evidence:
                    if isinstance(quote, str):
                        evidence_quote_total += 1
                        grounded = is_grounded(quote, decision_text)
                        evidence_grounded_total += int(grounded)
                        if not grounded:
                            errors.append(
                                {
                                    "item_id": item_id,
                                    "expected": "evidence quote grounded in decision_text",
                                    "actual": quote,
                                    "error_type": "evidence_not_grounded",
                                    "severity": "major",
                                    "notes": f"{trait_id} evidence quote was not found after quote, whitespace, and case normalization.",
                                }
                            )
                            row_errors.append("evidence_not_grounded")

        if gold_set == "quiz":
            target = item["gold"].get("target_trait")
            for trait_id in SCORED_TRAITS:
                gold_score, _ = _gold_score(gold_traits.get(trait_id))
                predicted = scores[trait_id]
                if trait_id == target:
                    quiz_non_null[trait_id].append(predicted is not None)
                    if gold_score is not None and predicted is not None:
                        quiz_pairs[trait_id].append((gold_score, predicted))
                        if score_band(gold_score) == score_band(predicted):
                            score_correct_item_ids.append(item_id)
                    if gold_score is not None and predicted is None:
                        errors.append(
                            {
                                "item_id": item_id,
                                "expected": gold_score,
                                "actual": None,
                                "error_type": "missed_signal",
                                "severity": "major",
                                "notes": f"Target trait {trait_id} was null.",
                            }
                        )
                        row_errors.append("missed_signal")
                    if gold_score is not None and predicted is not None:
                        difference = abs(score_band(gold_score) - score_band(predicted))
                        if difference:
                            severity = (
                                "minor" if difference == 1
                                else "major" if difference == 2
                                else "critical"
                            )
                            errors.append(
                                {
                                    "item_id": item_id,
                                    "expected": gold_score,
                                    "actual": predicted,
                                    "error_type": "score_deviation",
                                    "severity": severity,
                                    "notes": f"{trait_id} differs by {difference} score band(s).",
                                }
                            )
                            row_errors.append("score_deviation")
                        if (
                            ((gold_score < 0.5) != (predicted < 0.5))
                            and abs(gold_score - predicted) > 0.2
                        ):
                            errors.append(
                                {
                                    "item_id": item_id,
                                    "expected": gold_score,
                                    "actual": predicted,
                                    "error_type": "polarity_inversion",
                                    "severity": "critical",
                                    "notes": f"{trait_id} lies on the opposite side of 0.5 by more than 0.2.",
                                }
                            )
                            row_errors.append("polarity_inversion")
                        confidence = _trait_confidence(predicted_traits, trait_id)
                        if confidence is not None:
                            if difference == 0:
                                confidence_correct.append(confidence)
                            else:
                                confidence_wrong.append(confidence)
                            if confidence >= 0.8 and difference >= 2:
                                high_confidence_wrong.append((item_id, trait_id))
                                errors.append(
                                    {
                                        "item_id": item_id,
                                        "expected": f"within 1 score band of {gold_score}",
                                        "actual": predicted,
                                        "error_type": "confidence_miscalibration",
                                        "severity": "major",
                                        "notes": f"{trait_id} confidence was {confidence:.3f} with an error of at least 2 bands.",
                                    }
                                )
                                row_errors.append("confidence_miscalibration")
                elif predicted is not None:
                    evidence = predicted_traits.get(trait_id, {}).get("evidence", [])
                    grounded = bool(evidence) and all(
                        is_grounded(quote, decision_text)
                        for quote in evidence
                        if isinstance(quote, str)
                    )
                    quiz_off_target.append(
                        (item_id, trait_id, predicted, grounded)
                    )

            if response and response.get("extraction_status") != _expected_status(
                gold_traits
            ):
                errors.append(
                    {
                        "item_id": item_id,
                        "expected": _expected_status(gold_traits),
                        "actual": response.get("extraction_status"),
                        "error_type": "status_error",
                        "severity": "major",
                        "notes": "Model extraction_status disagrees with gold-derived status.",
                    }
                )
                row_errors.append("status_error")

        elif gold_set == "organic":
            ambiguous = bool(item["gold"].get("ambiguous_gold"))
            predicted_factor = bool(factors)
            gold_factor = item["gold"].get("situational_factor")
            if not ambiguous:
                for trait_id in SCORED_TRAITS:
                    gold_score, gold_confidence = _gold_score(
                        gold_traits.get(trait_id)
                    )
                    predicted = scores[trait_id]
                    if gold_score is not None:
                        if predicted is None:
                            organic_missed.append((item_id, trait_id))
                            errors.append(
                                {
                                    "item_id": item_id,
                                    "expected": gold_score,
                                    "actual": None,
                                    "error_type": "missed_signal",
                                    "severity": "major",
                                    "notes": f"Gold {trait_id} score is non-null but model score is null.",
                                }
                            )
                            row_errors.append("missed_signal")
                        else:
                            organic_pairs[trait_id].append((gold_score, predicted))
                            if score_band(gold_score) == score_band(predicted):
                                score_correct_item_ids.append(item_id)
                            confidence = _trait_confidence(predicted_traits, trait_id)
                            band_difference = abs(
                                score_band(gold_score) - score_band(predicted)
                            )
                            if band_difference:
                                severity = (
                                    "minor" if band_difference == 1
                                    else "major" if band_difference == 2
                                    else "critical"
                                )
                                errors.append(
                                    {
                                        "item_id": item_id,
                                        "expected": gold_score,
                                        "actual": predicted,
                                        "error_type": "score_deviation",
                                        "severity": severity,
                                        "notes": f"{trait_id} differs by {band_difference} score band(s).",
                                    }
                                )
                                row_errors.append("score_deviation")
                            if (
                                ((gold_score < 0.5) != (predicted < 0.5))
                                and abs(gold_score - predicted) > 0.2
                            ):
                                errors.append(
                                    {
                                        "item_id": item_id,
                                        "expected": gold_score,
                                        "actual": predicted,
                                        "error_type": "polarity_inversion",
                                        "severity": "critical",
                                        "notes": f"{trait_id} lies on the opposite side of 0.5 by more than 0.2.",
                                    }
                                )
                                row_errors.append("polarity_inversion")
                            if confidence is not None and gold_confidence is not None:
                                organic_confidence_errors.append(
                                    abs(confidence - gold_confidence)
                                )
                                if band_difference == 0:
                                    confidence_correct.append(confidence)
                                else:
                                    confidence_wrong.append(confidence)
                                if confidence >= 0.8 and band_difference >= 2:
                                    high_confidence_wrong.append((item_id, trait_id))
                                    errors.append(
                                        {
                                            "item_id": item_id,
                                            "expected": f"within 1 score band of {gold_score}",
                                            "actual": predicted,
                                            "error_type": "confidence_miscalibration",
                                            "severity": "major",
                                            "notes": f"{trait_id} confidence was {confidence:.3f} with an error of at least 2 bands.",
                                        }
                                    )
                                    row_errors.append("confidence_miscalibration")
                    elif predicted is not None:
                        organic_unsupported.append((item_id, trait_id))
                        errors.append(
                            {
                                "item_id": item_id,
                                "expected": None,
                                "actual": predicted,
                                "error_type": "unsupported_inference",
                                "severity": "major",
                                "notes": f"Gold {trait_id} is annotated null.",
                            }
                        )
                        row_errors.append("unsupported_inference")
                status_correct = bool(
                    response
                    and response.get("extraction_status")
                    == _expected_status(gold_traits)
                )
                organic_status.append(status_correct)
                if not status_correct:
                    errors.append(
                        {
                            "item_id": item_id,
                            "expected": _expected_status(gold_traits),
                            "actual": (
                                response.get("extraction_status")
                                if response
                                else outcome.failure_type
                            ),
                            "error_type": "status_error",
                            "severity": "major",
                            "notes": "Model extraction_status disagrees with gold-derived status.",
                        }
                    )
                    row_errors.append("status_error")
                factor_true_positive = predicted_factor and bool(gold_factor)
                organic_factor_counts["tp"] += int(factor_true_positive)
                organic_factor_counts["fp"] += int(
                    predicted_factor and not gold_factor
                )
                organic_factor_counts["fn"] += int(
                    not predicted_factor and bool(gold_factor)
                )
                if factor_true_positive:
                    predicted_category_matches = gold_factor.get("category") in factors
                    organic_factor_category.append(predicted_category_matches)
                    if not predicted_category_matches:
                        row_errors.append("context_confusion")
                        errors.append(
                            {
                                "item_id": item_id,
                                "expected": gold_factor,
                                "actual": factors,
                                "error_type": "context_confusion",
                                "severity": "major",
                                "notes": "Detected situational factor category does not match gold.",
                            }
                        )
                elif predicted_factor != bool(gold_factor):
                    row_errors.append("context_confusion")
                    errors.append(
                        {
                            "item_id": item_id,
                            "expected": gold_factor,
                            "actual": factors or None,
                            "error_type": "context_confusion",
                            "severity": "major",
                            "notes": "Situational factor was missed or hallucinated.",
                        }
                    )
                if gold_factor and gold_factor.get("category") == "external_constraint":
                    if any(scores[trait_id] is not None for trait_id in SCORED_TRAITS):
                        errors.append(
                            {
                                "item_id": item_id,
                                "expected": "external constraint not scored as a preference",
                                "actual": scores,
                                "error_type": "context_confusion",
                                "severity": "major",
                                "notes": "A trait received a score despite gold identifying an external constraint.",
                            }
                        )
                        row_errors.append("context_confusion")

                predicted_evidence = [
                    quote
                    for trait in predicted_traits.values()
                    for quote in trait.get("evidence", [])
                    if isinstance(quote, str)
                ]
                gold_evidence = item["gold"].get("evidence", [])
                organic_evidence_f1.append(
                    _token_f1(predicted_evidence, gold_evidence)
                )
            else:
                ambiguous_scores.append(
                    {
                        "item_id": item_id,
                        "predicted_scores": scores,
                        "predicted_confidence": {
                            trait_id: _trait_confidence(predicted_traits, trait_id)
                            for trait_id in SCORED_TRAITS
                        },
                        "model_status": response.get("extraction_status")
                        if response
                        else None,
                        "gold_traits": gold_traits,
                        "situational_factor": {
                            "gold": gold_factor,
                            "predicted": factors,
                        },
                        "evidence_grounding": [
                            {
                                "quote": quote,
                                "grounded": is_grounded(quote, decision_text),
                            }
                            for quote in (
                            quote
                            for trait in predicted_traits.values()
                            for quote in trait.get("evidence", [])
                            if isinstance(quote, str)
                            )
                        ],
                    }
                )
                for trait_id in SCORED_TRAITS:
                    gold_score, _ = _gold_score(gold_traits.get(trait_id))
                    predicted = scores[trait_id]
                    if gold_score is not None and predicted is not None:
                        organic_ambiguous_pairs[trait_id].append(
                            (gold_score, predicted)
                        )

        diagnostic_traits = _traits_by_id(diagnostic_responses[item_id])
        diagnostic_t06 = _trait_score(diagnostic_traits, "T06")
        if diagnostic_t06 is not None and not item["payload"].get(
            "context", {}
        ).get("history"):
            t06_violations.append(item_id)
            errors.append(
                {
                    "item_id": item_id,
                    "expected": None,
                    "actual": diagnostic_t06,
                    "error_type": "t06_violation",
                    "severity": "major",
                    "notes": "T06 is non-null without supplied history.",
                }
            )
            row_errors.append("t06_violation")

        if gold_set == "edge":
            expected = item["gold"].get("expected", {})
            checks = _expected_edge_checks(expected, response, predicted_traits)
            edge_checks.append((item_id, checks))
            for check_name, passed in checks.items():
                if not passed:
                    errors.append(
                        {
                            "item_id": item_id,
                            "expected": expected.get(f"expect_{check_name}"),
                            "actual": (
                                response.get("extraction_status")
                                if check_name == "status" and response
                                else scores
                            ),
                            "error_type": "edge_case_failure",
                            "severity": "major",
                            "notes": f"Edge expectation failed: {check_name}.",
                        }
                    )
                    row_errors.append("edge_case_failure")

        item_rows.append(
            {
                "item_id": item_id,
                "gold_set": gold_set,
                "split": item.get("split"),
                "target_trait": item.get("gold", {}).get("target_trait", ""),
                "strict_json_parse": outcome.failure_type
                not in {"empty_response", "not_json"},
                "schema_valid": not outcome.schema_errors
                and outcome.failure_type not in {"empty_response", "not_json"},
                "semantic_valid": outcome.valid,
                "recovered": outcome.recovered,
                "failure_type": outcome.failure_type or "",
                "gold_status": _expected_status(gold_traits),
                "model_status": response.get("extraction_status", "")
                if response
                else "",
                "score_errors": "|".join(sorted(set(row_errors))),
                **{
                    f"gold_score_{trait_id}": _gold_score(
                        gold_traits.get(trait_id)
                    )[0]
                    for trait_id in TRAIT_IDS
                },
                **{
                    f"gold_confidence_{trait_id}": _gold_score(
                        gold_traits.get(trait_id)
                    )[1]
                    for trait_id in TRAIT_IDS
                },
                **{f"score_{trait_id}": scores[trait_id] for trait_id in TRAIT_IDS},
            }
        )

    def rate(numerator: int, denominator: int) -> float | None:
        return _divide(numerator, denominator)

    total_responses = len(raw_rows)
    failure_counts = Counter(
        outcome.failure_type
        for outcome in validations.values()
        if outcome.failure_type is not None
    )
    strict_parses = sum(
        outcome.failure_type not in {"empty_response", "not_json"}
        for outcome in validations.values()
    )
    schema_valid_count = sum(
        not outcome.schema_errors
        and outcome.failure_type not in {"empty_response", "not_json"}
        for outcome in validations.values()
    )
    semantic_valid_count = sum(outcome.valid for outcome in validations.values())
    recovered_count = sum(outcome.recovered for outcome in validations.values())

    quiz_metrics: dict[str, Any] = {}
    all_quiz_pairs: list[tuple[float, float]] = []
    for trait_id in SCORED_TRAITS:
        all_quiz_pairs.extend(quiz_pairs[trait_id])
        quiz_metrics[trait_id] = {
            "target_non_null_rate": _mean(
                float(value) for value in quiz_non_null[trait_id]
            ),
            "target_n": len(quiz_non_null[trait_id]),
            **score_metrics(quiz_pairs[trait_id]),
        }
    quiz_metrics["overall"] = {
        "target_non_null_rate": _mean(
            float(value)
            for trait_values in quiz_non_null.values()
            for value in trait_values
        ),
        "target_n": sum(len(values) for values in quiz_non_null.values()),
        **score_metrics(all_quiz_pairs),
        "polarity_inversions_by_trait": {
            trait_id: quiz_metrics[trait_id]["polarity_inversions"]
            for trait_id in SCORED_TRAITS
        },
    }
    off_target_count = len(quiz_off_target)
    quiz_items_by_trait = {
        trait_id: sum(
            item["gold_set"] == "quiz"
            and item["item_id"] in raw_by_id
            and item["gold"].get("target_trait") != trait_id
            for item in items
        )
        for trait_id in SCORED_TRAITS
    }
    off_target_by_trait = {
        trait_id: {
            "non_null_count": sum(
                predicted_trait == trait_id
                for _, predicted_trait, _, _ in quiz_off_target
            ),
            "possible_count": quiz_items_by_trait[trait_id],
            "rate": _divide(
                sum(
                    predicted_trait == trait_id
                    for _, predicted_trait, _, _ in quiz_off_target
                ),
                quiz_items_by_trait[trait_id],
            ),
            "grounded_share": _divide(
                sum(
                    grounded
                    for _, predicted_trait, _, grounded in quiz_off_target
                    if predicted_trait == trait_id
                ),
                sum(
                    predicted_trait == trait_id
                    for _, predicted_trait, _, _ in quiz_off_target
                ),
            ),
        }
        for trait_id in SCORED_TRAITS
    }
    organic_metrics: dict[str, Any] = {}
    organic_all_pairs = [
        pair for values in organic_pairs.values() for pair in values
    ]
    for trait_id in SCORED_TRAITS:
        organic_metrics[trait_id] = score_metrics(organic_pairs[trait_id])
    organic_ambiguous_metrics = {
        trait_id: score_metrics(organic_ambiguous_pairs[trait_id], bootstrap=False)
        for trait_id in SCORED_TRAITS
    }
    organic_ambiguous_metrics["overall"] = score_metrics(
        [
            pair
            for values in organic_ambiguous_pairs.values()
            for pair in values
        ],
        bootstrap=False,
    )
    factor_tp = organic_factor_counts["tp"]
    factor_fp = organic_factor_counts["fp"]
    factor_fn = organic_factor_counts["fn"]
    organic_metrics["overall"] = {
        **score_metrics(organic_all_pairs),
        "missed_signal_rate": _divide(
            len(organic_missed),
            len(organic_missed) + len(organic_all_pairs),
        ),
        "missed_signal_count": len(organic_missed),
        "unsupported_inference_rate": _divide(
            len(organic_unsupported),
            len(organic_unsupported)
            + sum(
                1
                for item in items
                if item["gold_set"] == "organic"
                and item["item_id"] in raw_by_id
                and not item["gold"].get("ambiguous_gold")
                for trait_id, value in _gold_traits(item).items()
                if trait_id in SCORED_TRAITS
                if _gold_score(value)[0] is None
            ),
        ),
        "unsupported_inference_count": len(organic_unsupported),
        "status_accuracy": _mean(float(value) for value in organic_status),
        "situational_factor": {
            "precision": _divide(factor_tp, factor_tp + factor_fp),
            "recall": _divide(factor_tp, factor_tp + factor_fn),
            "category_agreement": _mean(
                float(value) for value in organic_factor_category
            ),
            "true_positive": factor_tp,
            "false_positive": factor_fp,
            "false_negative": factor_fn,
        },
        "confidence_mae": _mean(organic_confidence_errors),
        "confidence_n": len(organic_confidence_errors),
        "organic_evidence_token_overlap_f1_report_only": _mean(
            value for value in organic_evidence_f1 if value is not None
        ),
    }

    edge_expected_total = sum(len(checks) for _, checks in edge_checks)
    edge_passed_total = sum(
        sum(checks.values()) for _, checks in edge_checks
    )
    edge_failures = [
        {"item_id": item_id, "failed_checks": [
            name for name, passed in checks.items() if not passed
        ]}
        for item_id, checks in edge_checks
        if not all(checks.values())
    ]

    review_candidates = sorted(set(score_correct_item_ids))
    manually_review = random.Random(42).sample(
        review_candidates, min(10, len(review_candidates))
    )
    for item_id in manually_review:
        errors.append(
            {
                "item_id": item_id,
                "expected": "human review of evidence support",
                "actual": "target score in exact gold band",
                "error_type": "needs_manual_review",
                "severity": "review",
                "notes": "Sampled for independent cross-review; numeric score match does not establish evidence support.",
            }
        )

    metrics = {
        "response_count": total_responses,
        "format": {
            "strict_json_parse_rate": rate(strict_parses, total_responses),
            "schema_valid_rate": rate(schema_valid_count, total_responses),
            "semantic_valid_rate": rate(semantic_valid_count, total_responses),
            "recovered_rate": rate(recovered_count, total_responses),
            "failure_counts": dict(sorted(failure_counts.items())),
        },
        "quiz": {
            "target_trait_scoring": quiz_metrics,
            "off_target_extraction": {
                "non_null_count": off_target_count,
                "possible_count": sum(
                    5
                    for item in items
                    if item["gold_set"] == "quiz" and item["item_id"] in raw_by_id
                ),
                "rate": _divide(
                    off_target_count,
                    sum(
                        5
                        for item in items
                        if item["gold_set"] == "quiz"
                        and item["item_id"] in raw_by_id
                    ),
                ),
                "grounded_share": _divide(
                    sum(value[3] for value in quiz_off_target),
                    off_target_count,
                ),
                "by_trait": off_target_by_trait,
            },
        },
        "organic": {
            "score_metrics": organic_metrics,
            "ambiguous_gold_item_count": len(ambiguous_scores),
            "ambiguous_gold_separate": ambiguous_scores,
            "ambiguous_gold_score_metrics": organic_ambiguous_metrics,
        },
        "evidence": {
            "grounding_rate": _divide(
                evidence_grounded_total, evidence_quote_total
            ),
            "grounded_quotes": evidence_grounded_total,
            "quote_count": evidence_quote_total,
            "quiz_gold_evidence_text_match": "not_applicable: quiz evidence is templated",
        },
        "confidence": {
            "scored_trait_confidence_count": len(confidence_values),
            "mean": _mean(confidence_values),
            "bins": {
                "[0.0,0.2)": sum(value < 0.2 for value in confidence_values),
                "[0.2,0.4)": sum(0.2 <= value < 0.4 for value in confidence_values),
                "[0.4,0.6)": sum(0.4 <= value < 0.6 for value in confidence_values),
                "[0.6,0.8)": sum(0.6 <= value < 0.8 for value in confidence_values),
                "[0.8,1.0]": sum(0.8 <= value <= 1.0 for value in confidence_values),
            },
            "mean_when_band_correct": _mean(confidence_correct),
            "mean_when_band_wrong": _mean(confidence_wrong),
            "high_confidence_wrong_count": len(high_confidence_wrong),
            "high_confidence_wrong_rate": _divide(
                len(high_confidence_wrong),
                len(confidence_values),
            ),
        },
        "edge_cases": {
            "passed_checks": edge_passed_total,
            "total_checks": edge_expected_total,
            "pass_rate": _divide(edge_passed_total, edge_expected_total),
            "item_checks": [
                {"item_id": item_id, **checks} for item_id, checks in edge_checks
            ],
            "failures": edge_failures,
        },
        "t06_violations": {
            "count": len(t06_violations),
            "item_ids": t06_violations,
        },
        "errors_by_type": dict(
            sorted(Counter(error["error_type"] for error in errors).items())
        ),
        "errors_by_severity": dict(
            sorted(Counter(error["severity"] for error in errors).items())
        ),
        "manual_review_sample": manually_review,
        "readiness_criteria": {},
    }
    criteria = [
        (
            "strict_schema_valid_rate",
            metrics["format"]["schema_valid_rate"],
            0.95,
            "at_least",
        ),
        (
            "schema_valid_or_recovered_rate",
            _divide(schema_valid_count + recovered_count, total_responses),
            0.99,
            "at_least",
        ),
        (
            "quiz_target_non_null_rate",
            quiz_metrics["overall"]["target_non_null_rate"],
            0.90,
            "at_least",
        ),
        (
            "quiz_exact_band_accuracy",
            quiz_metrics["overall"]["exact_band_accuracy"],
            0.60,
            "at_least",
        ),
        (
            "quiz_within_one_band_rate",
            quiz_metrics["overall"]["within_one_band_rate"],
            0.90,
            "at_least",
        ),
        ("quiz_mae", quiz_metrics["overall"]["mae"], 0.15, "at_most"),
        (
            "quiz_direction_accuracy",
            quiz_metrics["overall"]["direction_accuracy"],
            0.90,
            "at_least",
        ),
        (
            "quiz_spearman_rho",
            quiz_metrics["overall"]["spearman_rho"],
            0.80,
            "at_least",
        ),
        (
            "quiz_polarity_inversion_rate",
            quiz_metrics["overall"]["polarity_inversion_rate"],
            0.02,
            "at_most",
        ),
        (
            "evidence_grounding_rate",
            metrics["evidence"]["grounding_rate"],
            0.98,
            "at_least",
        ),
        ("t06_violations", len(t06_violations), 0, "equal"),
        (
            "edge_case_pass_rate",
            metrics["edge_cases"]["pass_rate"],
            0.80,
            "at_least",
        ),
        (
            "organic_situational_factor_recall",
            organic_metrics["overall"]["situational_factor"]["recall"],
            0.80,
            "at_least",
        ),
    ]
    for name, observed, threshold, comparison in criteria:
        if observed is None:
            status = "not_applicable"
        elif comparison == "at_least":
            status = "pass" if observed >= threshold else "fail"
        elif comparison == "at_most":
            status = "pass" if observed <= threshold else "fail"
        else:
            status = "pass" if observed == threshold else "fail"
        metrics["readiness_criteria"][name] = {
            "observed": observed,
            "operator": comparison,
            "threshold": threshold,
            "status": status,
            "approval": "proposed — pending team lead approval",
        }
    return {
        "metrics": metrics,
        "compliance": compliance,
        "items": item_rows,
        "errors": errors,
        "validations": validations,
        "responses": parsed_responses,
    }
