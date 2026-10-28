from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "docs" / "tasks" / "task-4-llm-extraction"
RESULTS_DIR = ROOT / "evaluation" / "results"
RUNS_DIR = ROOT / "evaluation" / "runs"
DEV_ID = "v2.0__openai-gpt-oss-120b__all-dev__5825600d"
HELDOUT_ID = "v2.0__openai-gpt-oss-120b__all-heldout__5825600d"
CANDIDATE_ID = "v2.1__openai-gpt-oss-120b__all-dev__5825600d"
PROMPT_SHA256 = "6f93b33da4bf2193641bb47156b1ca090a84f86f718e69085513aae4e6d280d7"
PROMPT_REGISTRY_PATH = ROOT / "prompts" / "extraction" / "registry.json"
RATE_CRITERIA = {
    "strict_schema_valid_rate",
    "schema_valid_or_recovered_rate",
    "quiz_target_non_null_rate",
    "quiz_exact_band_accuracy",
    "quiz_within_one_band_rate",
    "quiz_direction_accuracy",
    "quiz_polarity_inversion_rate",
    "evidence_grounding_rate",
    "edge_case_pass_rate",
    "organic_situational_factor_recall",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_metrics(run_id: str) -> dict[str, Any]:
    return read_json(RESULTS_DIR / run_id / "metrics.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentage(value: float | int | None, digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{100 * value:.{digits}f}%"


def number(value: float | int | None, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def interval(metric: dict[str, Any], key: str, *, is_percent: bool = False) -> str:
    ci = metric["bootstrap_95_ci"][key]
    render = percentage if is_percent else number
    return f"[{render(ci['lower'])}, {render(ci['upper'])}]"


def load_run(
    run_id: str, *, expected_prompt_sha256: str | None = PROMPT_SHA256
) -> tuple[dict[str, Any], dict[str, Any]]:
    metrics = read_metrics(run_id)
    manifest = read_json(RUNS_DIR / run_id / "manifest.json")
    if metrics["run"]["run_id"] != run_id or manifest["run_id"] != run_id:
        raise ValueError(f"Run ID mismatch for {run_id}")
    if (
        expected_prompt_sha256 is not None
        and metrics["run"]["prompt_sha256"] != expected_prompt_sha256
    ):
        raise ValueError(f"Unexpected prompt hash for {run_id}")
    return metrics, manifest


def validate_frozen_status() -> None:
    registry = read_json(PROMPT_REGISTRY_PATH)
    prompt = next(item for item in registry["prompts"] if item["version"] == "v2.0")
    if prompt["status"] != "frozen" or prompt["sha256"] != PROMPT_SHA256:
        raise ValueError("v2.0 is not registered as frozen with the expected hash")
    for spec in ("01_input_spec.md", "02_output_spec.md"):
        text = (TASK_DIR / spec).read_text(encoding="utf-8")
        if "Contract v1.0 is frozen." not in text:
            raise ValueError(f"{spec} does not affirm the frozen v1.0 contract")


def render_trait_table(dev: dict[str, Any], heldout: dict[str, Any]) -> str:
    rows = [
        "| Trait | Dev paired / target N | Dev non-null | Dev MAE [95% CI] | "
        "Dev exact band [95% CI] | Dev within 1 band | Dev QWK | Dev Spearman [95% CI] | "
        "Dev direction | Dev inversions | "
        "Held-out paired / target N | Held-out non-null | Held-out MAE [95% CI] | "
        "Held-out exact band [95% CI] | Held-out within 1 band | Held-out QWK | "
        "Held-out Spearman [95% CI] | Held-out direction | Held-out inversions |",
        "| " + " | ".join(["---"] * 19) + " |",
    ]
    for trait in ("T01", "T02", "T03", "T04", "T05", "overall"):
        cells = [trait]
        for metrics in (dev, heldout):
            item = metrics["quiz"]["target_trait_scoring"][trait]
            cells.extend(
                [
                    f"{item['n_paired_scores']} / {item['target_n']}",
                    percentage(item["target_non_null_rate"]),
                    f"{number(item['mae'])} {interval(item, 'mae')}",
                    f"{percentage(item['exact_band_accuracy'])} "
                    f"{interval(item, 'accuracy', is_percent=True)}",
                    percentage(item["within_one_band_rate"]),
                    number(item["quadratic_weighted_kappa"]),
                    f"{number(item['spearman_rho'])} {interval(item, 'rho')}",
                    percentage(item["direction_accuracy"]),
                    str(item["polarity_inversions"]),
                ]
            )
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def criterion_observed(name: str, data: dict[str, Any]) -> str:
    value = data.get("observed")
    if value is None:
        return "n/a"
    if name in RATE_CRITERIA:
        return percentage(value)
    if name in {"quiz_mae", "quiz_spearman_rho"}:
        return number(value)
    return str(value)


CRITERION_LABELS = {
    "strict_schema_valid_rate": "Strict schema-valid rate",
    "schema_valid_or_recovered_rate": "Schema-valid or recovered diagnostic rate",
    "quiz_target_non_null_rate": "Quiz target non-null rate",
    "quiz_exact_band_accuracy": "Quiz exact-band accuracy",
    "quiz_within_one_band_rate": "Quiz within-one-band rate",
    "quiz_mae": "Quiz MAE",
    "quiz_direction_accuracy": "Quiz direction accuracy",
    "quiz_spearman_rho": "Quiz Spearman rho",
    "quiz_polarity_inversion_rate": "Quiz polarity-inversion rate",
    "evidence_grounding_rate": "Evidence grounding",
    "t06_violations": "T06 violations",
    "edge_case_pass_rate": "Edge-case pass rate",
    "organic_situational_factor_recall": "Organic situational-factor recall",
}


def render_criteria(dev: dict[str, Any], heldout: dict[str, Any]) -> str:
    rows = [
        "| Criterion | Threshold | Dev | Held-out | Dev result | Held-out result |",
        "|---|---:|---:|---:|---|---|",
    ]
    for name, label in CRITERION_LABELS.items():
        left = dev["readiness_criteria"][name]
        right = heldout["readiness_criteria"][name]
        operator = {"at_least": "≥", "at_most": "≤", "equal": "="}[left["operator"]]
        if name in RATE_CRITERIA:
            threshold = percentage(left["threshold"])
        elif name in {"quiz_mae", "quiz_spearman_rho"}:
            threshold = number(left["threshold"])
        else:
            threshold = str(left["threshold"])
        rows.append(
            f"| {label} | {operator} {threshold} | "
            f"{criterion_observed(name, left)} | {criterion_observed(name, right)} | "
            f"{left['status']} | {right['status']} |"
        )
    return "\n".join(rows)


def render_progression(dev: dict[str, Any], candidate: dict[str, Any]) -> str:
    v20 = dev["quiz"]["target_trait_scoring"]["overall"]
    v21 = candidate["quiz"]["target_trait_scoring"]["overall"]
    org20 = dev["organic"]["score_metrics"]["overall"]
    org21 = candidate["organic"]["score_metrics"]["overall"]
    edge20 = dev["edge_cases"]
    edge21 = candidate["edge_cases"]
    rows = [
        "| Dev metric | v2.0 frozen baseline | v2.1 rejected candidate |",
        "|---|---:|---:|",
        f"| Quiz exact-band accuracy | {percentage(v20['exact_band_accuracy'])} | "
        f"{percentage(v21['exact_band_accuracy'])} |",
        f"| Quiz MAE | {number(v20['mae'])} | {number(v21['mae'])} |",
        f"| Quiz Spearman rho | {number(v20['spearman_rho'])} | "
        f"{number(v21['spearman_rho'])} |",
        f"| Organic situational-factor recall | "
        f"{percentage(org20['situational_factor']['recall'])} | "
        f"{percentage(org21['situational_factor']['recall'])} |",
        f"| Organic situational-factor precision | "
        f"{percentage(org20['situational_factor']['precision'])} | "
        f"{percentage(org21['situational_factor']['precision'])} |",
        f"| Organic factor category agreement | "
        f"{percentage(org20['situational_factor']['category_agreement'])} | "
        f"{percentage(org21['situational_factor']['category_agreement'])} |",
        f"| Edge-case checks | {edge20['passed_checks']}/{edge20['total_checks']} "
        f"({percentage(edge20['pass_rate'])}) | "
        f"{edge21['passed_checks']}/{edge21['total_checks']} "
        f"({percentage(edge21['pass_rate'])}) |",
    ]
    return "\n".join(rows)


def render_organic(dev: dict[str, Any], heldout: dict[str, Any]) -> str:
    rows = [
        "| Organic metric | Dev | Held-out |",
        "|---|---:|---:|",
    ]
    for key, label, is_percent in (
        ("n_paired_scores", "Paired numeric scores", False),
        ("mae", "MAE [95% CI]", False),
        ("exact_band_accuracy", "Exact band accuracy [95% CI]", True),
        ("missed_signal_rate", "Missed-signal rate", True),
        ("unsupported_inference_rate", "Unsupported-inference rate", True),
        ("status_accuracy", "Status accuracy", True),
        ("confidence_mae", "Confidence MAE", False),
        ("organic_evidence_token_overlap_f1_report_only", "Evidence token-overlap F1 (report-only)", False),
    ):
        left = dev["organic"]["score_metrics"]["overall"]
        right = heldout["organic"]["score_metrics"]["overall"]
        lv, rv = left.get(key), right.get(key)
        if key == "mae":
            lv = f"{number(lv)} {interval(left, 'mae')}"
            rv = f"{number(rv)} {interval(right, 'mae')}"
        elif key == "exact_band_accuracy":
            lv = f"{percentage(lv)} {interval(left, 'accuracy', is_percent=True)}"
            rv = f"{percentage(rv)} {interval(right, 'accuracy', is_percent=True)}"
        elif key == "n_paired_scores":
            lv, rv = str(lv), str(rv)
        elif is_percent:
            lv, rv = percentage(lv), percentage(rv)
        else:
            lv, rv = number(lv), number(rv)
        rows.append(f"| {label} | {lv} | {rv} |")

    for metric, label in (
        ("precision", "Situational-factor precision"),
        ("recall", "Situational-factor recall"),
        ("category_agreement", "Situational-factor category agreement"),
    ):
        left = dev["organic"]["score_metrics"]["overall"]["situational_factor"]
        right = heldout["organic"]["score_metrics"]["overall"]["situational_factor"]
        rows.append(
            f"| {label} | {percentage(left[metric])} "
            f"(TP {left['true_positive']}, FP {left['false_positive']}, "
            f"FN {left['false_negative']}) | {percentage(right[metric])} "
            f"(TP {right['true_positive']}, FP {right['false_positive']}, "
            f"FN {right['false_negative']}) |"
        )
    return "\n".join(rows)


def render_organic_trait_table(dev: dict[str, Any], heldout: dict[str, Any]) -> str:
    rows = [
        "| Trait | Dev paired N | Dev MAE [95% CI] | Dev exact band [95% CI] | "
        "Dev within 1 band | Dev QWK | Dev Spearman [95% CI] | Dev direction | "
        "Held-out paired N | Held-out MAE [95% CI] | Held-out exact band [95% CI] | "
        "Held-out within 1 band | Held-out QWK | Held-out Spearman [95% CI] | Held-out direction |",
        "| " + " | ".join(["---"] * 15) + " |",
    ]
    for trait in ("T01", "T02", "T03", "T04", "T05", "overall"):
        cells = [trait]
        for metrics in (dev, heldout):
            item = metrics["organic"]["score_metrics"][trait]
            cells.extend(
                [
                    str(item["n_paired_scores"]),
                    f"{number(item['mae'])} {interval(item, 'mae')}",
                    f"{percentage(item['exact_band_accuracy'])} "
                    f"{interval(item, 'accuracy', is_percent=True)}",
                    percentage(item["within_one_band_rate"]),
                    number(item["quadratic_weighted_kappa"]),
                    f"{number(item['spearman_rho'])} {interval(item, 'rho')}",
                    percentage(item["direction_accuracy"]),
                ]
            )
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def render_ambiguous(dev: dict[str, Any], heldout: dict[str, Any]) -> str:
    rows = [
        "| Split | Item IDs (`ambiguous_gold`) | Trait | Paired N | MAE | Exact band |",
        "|---|---|---|---:|---:|---:|",
    ]
    for split_name, metrics in (("Dev", dev), ("Held-out", heldout)):
        organic = metrics["organic"]
        ids = ", ".join(item["item_id"] for item in organic["ambiguous_gold_separate"])
        if not ids:
            rows.append(f"| {split_name} | none | — | — | — | — |")
            continue
        by_trait = organic["ambiguous_gold_score_metrics"]
        for trait, item in by_trait.items():
            rows.append(
                f"| {split_name} | {ids} | {trait} | {item['n_paired_scores']} | "
                f"{number(item.get('mae'))} | {percentage(item.get('exact_band_accuracy'))} |"
            )
    return "\n".join(rows)


ERROR_MEANINGS = {
    "malformed_output": "Empty/non-JSON output or schema/semantic validation failure.",
    "missed_signal": "A gold-supported organic or quiz target trait was returned null.",
    "unsupported_inference": "A score was emitted for a gold-null organic trait.",
    "polarity_inversion": "Prediction is on the opposite side of 0.5 by more than 0.2.",
    "score_deviation": "Paired numeric score differs by one or more score bands.",
    "evidence_not_grounded": "Evidence quote was not found in normalized input text.",
    "context_confusion": "Situational factor is missed, hallucinated, miscategorized, or a constraint is scored as a trait.",
    "confidence_miscalibration": "Confidence is at least 0.8 with an error of two or more bands.",
    "status_error": "Output status differs from status implied by the gold.",
    "t06_violation": "T06 is non-null without supplied history.",
    "edge_case_failure": "A qualitative edge expectation check failed.",
    "needs_manual_review": "Deterministic cross-review flag; not an automated finding.",
}


def render_errors(dev: dict[str, Any], heldout: dict[str, Any]) -> str:
    names = list(ERROR_MEANINGS)
    names.extend(
        name
        for name in sorted(set(dev["errors_by_type"]) | set(heldout["errors_by_type"]))
        if name not in names
    )
    rows = [
        "| Error category | Dev count | Held-out count | Meaning |",
        "|---|---:|---:|---|",
    ]
    for name in names:
        left = dev["errors_by_type"].get(name, 0)
        right = heldout["errors_by_type"].get(name, 0)
        rows.append(
            f"| `{name}` | {left} | {right} | "
            f"{ERROR_MEANINGS.get(name, 'See the evaluation taxonomy in 04_evaluation_method.md.')} |"
        )
    return "\n".join(rows)


def raw_records(run_id: str) -> dict[str, dict[str, Any]]:
    path = RUNS_DIR / run_id / "raw_responses.jsonl"
    return {
        row["item_id"]: row
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
        for row in [json.loads(line)]
    }


def case_block(
    title: str,
    item: dict[str, Any],
    raw: dict[str, Any],
    explanation: str,
) -> str:
    payload = item["payload"]
    gold = item["gold"]
    return "\n".join(
        [
            f"### {title}",
            "",
            explanation,
            "",
            "**Raw input (`decision_text`):**",
            "",
            "```text",
            payload["decision_text"],
            "```",
            "",
            "**Gold annotation:**",
            "",
            "```json",
            json.dumps(gold, ensure_ascii=False, indent=2),
            "```",
            "",
            "**Raw model output (`response_text`):**",
            "",
            "```json",
            raw["response_text"],
            "```",
        ]
    )


def select_exact_quiz_case(
    eval_items: list[dict[str, Any]], raw_by_run: dict[str, dict[str, dict[str, Any]]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    for item in eval_items:
        if item["gold_set"] != "quiz" or item["split"] != "dev":
            continue
        raw = raw_by_run[DEV_ID].get(item["item_id"])
        if not raw:
            continue
        target = item["gold"]["target_trait"]
        gold_score = item["gold"]["traits"][target]["value"]
        try:
            output = json.loads(raw["response_text"])
        except json.JSONDecodeError:
            continue
        predicted = next(
            trait["score"] for trait in output["traits"] if trait["trait_id"] == target
        )
        if gold_score is not None and predicted is not None:
            if min(int(gold_score * 5), 4) == min(int(predicted * 5), 4):
                return item, raw
    raise ValueError("Could not find a score-band-correct dev quiz example")


def render_cases(
    eval_items: list[dict[str, Any]],
    dev: dict[str, Any],
    heldout: dict[str, Any],
) -> str:
    by_id = {item["item_id"]: item for item in eval_items}
    raw_by_run = {DEV_ID: raw_records(DEV_ID), HELDOUT_ID: raw_records(HELDOUT_ID)}
    correct_item, correct_raw = select_exact_quiz_case(eval_items, raw_by_run)
    blocks = [
        case_block(
            f"Correct by target score band: {correct_item['item_id']}",
            correct_item,
            correct_raw,
            "The target-trait prediction is in the same score band as its numeric quiz gold. "
            "This is score agreement, not independent evidence-quality adjudication.",
        )
    ]
    for item_id, run_id, explanation in (
        (
            "EDGE03",
            DEV_ID,
            "The dev-only self-authored expectation required all traits null, a situational factor, "
            "and low confidence. The recorded output incorrectly scored T05 from a budget constraint.",
        ),
        (
            "Q01_A",
            HELDOUT_ID,
            "Held-out quiz target T01 has a numeric gold score, but the model returned null "
            "(missed signal and status error).",
        ),
    ):
        blocks.append(
            case_block(
                f"Incorrect case: {item_id}",
                by_id[item_id],
                raw_by_run[run_id][item_id],
                explanation,
            )
        )
    return "\n\n".join(blocks)


def render_edge_results(
    dev: dict[str, Any], heldout: dict[str, Any]
) -> str:
    edge = dev["edge_cases"]
    heldout_edge = heldout["edge_cases"]
    rows = [
        "| Split | Checks passed | Checks total | Pass rate | Failed items |",
        "|---|---:|---:|---:|---|",
    ]
    for label, item in (("Dev", edge),):
        failures = ", ".join(
            failure["item_id"] for failure in item["failures"]
        ) or "none"
        rows.append(
            f"| {label} | {item['passed_checks']} | {item['total_checks']} | "
            f"{percentage(item['pass_rate'])} | {failures} |"
        )
    rows.append(
        f"| Held-out | {heldout_edge['passed_checks']} | {heldout_edge['total_checks']} | "
        f"{percentage(heldout_edge['pass_rate'])} | No edge records in held-out split |"
    )
    return "\n".join(rows)


def create_report(
    dev: dict[str, Any],
    dev_manifest: dict[str, Any],
    heldout: dict[str, Any],
    heldout_manifest: dict[str, Any],
    candidate: dict[str, Any],
) -> str:
    dataset_manifest = read_json(ROOT / "data" / "processed" / "MANIFEST.json")
    split = read_json(ROOT / "data" / "processed" / "split_v1.json")
    eval_items = read_json(ROOT / "data" / "processed" / "eval_set_v1.json")
    quiz_gold = read_json(ROOT / "data" / "gold" / "quiz_gold_v1.0.json")
    organic_gold = read_json(ROOT / "data" / "gold" / "organic_gold_v1.0.json")
    edge_gold = read_json(ROOT / "data" / "gold" / "edge_cases_v1.0.json")
    source_hashes = dataset_manifest["files"]
    eval_by_set = {
        name: sum(item["gold_set"] == name for item in eval_items)
        for name in ("quiz", "organic", "edge")
    }
    split_counts = {
        name: {
            "dev": len(split[name]["dev"]),
            "heldout": len(split[name]["heldout"]),
        }
        for name in ("quiz", "organic", "edge")
    }
    languages = sorted({item["payload"].get("language", "en") for item in eval_items})
    ambiguous_ids = {
        label: [
            item["item_id"]
            for item in metrics["organic"]["ambiguous_gold_separate"]
        ]
        for label, metrics in (("dev", dev), ("heldout", heldout))
    }
    dev_batches = math.ceil(dev["response_count"] / dev_manifest["batch_size"])
    heldout_batches = math.ceil(heldout["response_count"] / heldout_manifest["batch_size"])
    prompt_text = (ROOT / "prompts" / "extraction" / "extraction_v2.0.md").read_text(
        encoding="utf-8"
    )
    report_cases = render_cases(eval_items, dev, heldout)
    org14 = next(item for item in eval_items if item["item_id"] == "ORG14")
    org14_t06 = org14["gold"]["traits"]["T06"]["value"]

    return f"""# Task 4.5 — Evaluation report

**Report generated:** {datetime.now().date().isoformat()}  
**Decision:** Ready with conditions  
**Frozen prompt:** v2.0

## 1. Purpose and scope

Task 4 implements and evaluates extraction of structured, evidence-supported T01–T06 traits from onboarding-quiz answers and organic decision narratives. It covers frozen input/output contracts, prompt versioning, a resumable inference runner, offline strict validation, gold-linked evaluation, error analysis, and a handoff contract for downstream profile aggregation. It does **not** establish clinical validity, population-level generalization, calibrated confidence, longitudinal self-consistency, or production fitness.

## 2. Datasets used

| Dataset | Records | Split | SHA-256 |
|---|---:|---|---|
| Quiz gold v1.0 | {len(quiz_gold['records'])} | {split_counts['quiz']['dev']} dev / {split_counts['quiz']['heldout']} held-out | `{source_hashes['data/gold/quiz_gold_v1.0.json']}` |
| Organic gold v1.0 | {len(organic_gold['records'])} | {split_counts['organic']['dev']} dev / {split_counts['organic']['heldout']} held-out | `{source_hashes['data/gold/organic_gold_v1.0.json']}` |
| Self-authored edge cases v1.0 | {len(edge_gold['records'])} | {split_counts['edge']['dev']} dev / {split_counts['edge']['heldout']} held-out | `{source_hashes['data/gold/edge_cases_v1.0.json']}` |
| Unified evaluation set v1 | {len(eval_items)} | {dev['response_count']} dev / {heldout['response_count']} held-out evaluated | `{source_hashes['data/processed/eval_set_v1.json']}` |
| Frozen split v1 | — | seed {split['header']['seed']} | `{source_hashes['data/processed/split_v1.json']}` |

{split['header']['method']}

This fixed split is used to reserve held-out examples from prompt iteration. Quiz options from one question stay together to avoid answer-option leakage; organic held-out records include both ontology edge-case-linked and other records; all self-authored edge records remain dev-only.

## 3. Experimental setup

| Setting | Value |
|---|---|
| Provider | Groq |
| Model | `{dev_manifest['model']}` |
| Temperature | {dev_manifest['temperature']} |
| Reasoning effort | `{dev_manifest['reasoning_effort']}` |
| Maximum completion tokens | {dev_manifest['max_completion_tokens']} |
| Prompt version | `{dev_manifest['prompt_version']}` (registry status: frozen) |
| Prompt SHA-256 | `{dev_manifest['prompt_sha256']}` |
| Contract version | v1.0 (input and output contracts frozen) |
| Evaluation-set SHA-256 | `{dev_manifest['eval_set_sha256']}` |
| Dev run ID / date | `{dev_manifest['run_id']}` / {dev_manifest['created_at'][:10]} |
| Held-out run ID / date | `{heldout_manifest['run_id']}` / {heldout_manifest['created_at'][:10]} |
| Run count | One logical run per split; {dev_batches} dev and {heldout_batches} held-out API batches; {dev['response_count']} and {heldout['response_count']} responses |
| Request format | JSON object |

The evaluated v2.0 prompt content is read from [`extraction_v2.0.md`](../../../prompts/extraction/extraction_v2.0.md); its byte-level SHA-256 is listed above. The only other version shown in the dev progression below is v2.1, a rejected candidate; it is not a final or held-out result.

## 4. Evaluation procedure

Evaluation is offline: the evaluator joins saved raw responses to the frozen evaluation set and gold by item ID, performs strict JSON parsing, schema validation, and semantic validation, and never edits or substitutes model output. Recovered/lenient parses remain failures. Ambiguous-gold organic records are excluded from headline organic metrics and shown separately below.

The evidence quote normalizer was corrected **after dev results were observed** to strip balanced surrounding quote delimiters (as well as normalize whitespace, typographic quotes, and case). The corrected evaluator was applied to all runs, and the change has a regression test (`test_grounding_accepts_balanced_quote_delimiters_around_excerpt`). The v2.0 raw responses, prompt, gold, and eval set were not changed by that correction.

## 5. Metrics

Metric definitions and denominators follow [`04_evaluation_method.md`](./04_evaluation_method.md). Quiz scores are compared only for paired numeric target traits; target non-null coverage and missed signals are separately reported. Per-trait and overall quiz 95% intervals are percentile bootstrap intervals (2,000 replicates, seed 42) for MAE, exact-band accuracy, and Spearman rho. Organic metrics exclude ambiguous-gold records from headline calculations. Evidence grounding is quote-level input-text grounding; organic evidence-token overlap is report-only. Edge-case pass rate is passed qualitative checks divided by defined checks. T06 violations count non-null T06 predictions without history.

## 6. Results

### Quiz target-trait results, v2.0

N columns show paired numeric scores / target items. Confidence intervals are 95% bootstrap intervals; score metrics and all point estimates are generated from each run's `metrics.json`.

{render_trait_table(dev, heldout)}

### Organic results, v2.0

Per-trait numeric score agreement (paired non-null gold/model scores):

{render_organic_trait_table(dev, heldout)}

Pooled organic diagnostics and factor results:

{render_organic(dev, heldout)}

The organic held-out set contains only {split_counts['organic']['heldout']} records. Its estimates—including situational-factor recall ({percentage(heldout['organic']['score_metrics']['overall']['situational_factor']['recall'])})—are **not statistically meaningful** and must not be interpreted as stable rates.

### Prompt-version progression on dev only

{render_progression(dev, candidate)}

v2.1 is rejected, not a final prompt: as documented in [`05_error_analysis.md`](./05_error_analysis.md), its clarifying change reduced eligible organic situational-factor recall below the registered threshold by missing ORG11. Despite better quiz and edge metrics, v2.1 is retained only as a draft. The official final evaluated pair is v2.0 dev and v2.0 held-out.

### Ambiguous gold, separately reported

These items are excluded from headline organic metrics. The per-trait values below are calculated from the evaluator's `ambiguous_gold_score_metrics`; they are not pooled with the headline results.

{render_ambiguous(dev, heldout)}

Dev ambiguous item IDs: {', '.join(ambiguous_ids['dev']) or 'none'}. Held-out ambiguous item IDs: {', '.join(ambiguous_ids['heldout']) or 'none'}.

## 7. Pre-registered criteria

The thresholds remain proposed and pending team-lead approval, as stated in the evaluation method. Criterion observations and pass/fail statuses below are read from the two final v2.0 `metrics.json` files; `not_applicable` is not counted as a pass.

{render_criteria(dev, heldout)}

## 8. Representative correct and incorrect cases and edge-case results

The following input, gold, and model-output blocks are reproduced from the frozen eval set and the saved runs' raw `response_text` values. The correct case means correct by score band only; evidence quality still needs human review.

{report_cases}

### Edge-case results

{render_edge_results(dev, heldout)}

Edge cases exist **only in the dev split** and are self-authored. The held-out split has no edge cases, so the edge pass rate has no held-out counterpart.

## 9. Error categories

Counts are error-log rows; a single item may contribute multiple rows. `needs_manual_review` is a reviewer flag, not an automated error finding.

{render_errors(dev, heldout)}

The main observed failure patterns are score compression toward interior bands, unsupported trait scoring, and confusion between situational circumstances and stable traits. Situational-factor category agreement is weak even where the binary factor-presence metric passes; see the dev error analysis for item-level diagnoses.

## 10. Limitations

- These results use one model from one provider (`{dev_manifest['model']}` on Groq). The team's earlier ChatGPT tests are not comparable because the model/provider and evaluation conditions differ.
- Quiz gold confidence is uniformly 0.70 and the source has a documented 0.70/0.90 inconsistency; confidence agreement is not a strong calibration claim. Quiz evidence is templated.
- There are only {len(organic_gold['records'])} organic gold items, with {split_counts['organic']['heldout']} held out; organic held-out metrics, including situational-factor recall, have very wide uncertainty and are not statistically meaningful.
- Edge cases are self-authored qualitative expectations and exist only in dev.
- Organic dev metrics were visible during prompt iteration; the v2.1 candidate was rejected on dev evidence. Held-out results were reserved for evaluation of the selected v2.0 prompt, not used for prompt revisions.
- Free-tier quota and rate-limit constraints limited the practical number and timing of API runs.
- Evaluation language(s): {', '.join(languages)}.{" English only." if languages == ["en"] else ""}
- Quiz answers are much easier and shorter than real narratives, so quiz performance likely overstates real-world accuracy.
- Gold annotations have known ambiguities. `ORG14` gold assigns T06={org14_t06}, but T06 is excluded from score comparison because the contract requires null without supplied history; the model's null is contract-compliant.
- Strict schema validity and grounded quotations do not prove that the interpretation is correct. The dev run contains {dev['errors_by_type'].get('needs_manual_review', 0)} deterministic manual-review flags, and human evidence cross-review remains outstanding.

## 11. Readiness decision

**Decision: Ready with conditions** for a limited, guarded downstream profile-aggregation pilot—not for unsupervised or high-impact use.

All applicable pre-registered numeric criteria pass on the final v2.0 dev and held-out runs. This is a positive engineering readiness signal, not validation. Conditions are: (1) team-lead approval of the proposed thresholds and this report; (2) human cross-review of evidence support before trusting aggregated profiles; (3) do not treat confidence as calibrated probability; (4) keep T06 null until longitudinal history is supplied under a later contract; and (5) preserve the situational-factor down-weighting and known-failure safeguards in the handoff. Organic held-out and edge-case evidence is too small to support an unconditional readiness claim.

**Approval:** ______________________________ (name)  **Date:** __________________

## 12. Reproduction steps

From a fresh clone on Windows PowerShell, use the project's pinned environment and the saved runs. These commands do not call the API. Using the venv's Python executable directly avoids PowerShell script-execution-policy differences:

```powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe -m pip install -e .
.\\.venv\\Scripts\\python.exe -m pytest -q
.\\.venv\\Scripts\\python.exe scripts\\evaluate_run.py --run-id {DEV_ID}
.\\.venv\\Scripts\\python.exe scripts\\evaluate_run.py --run-id {HELDOUT_ID}
```

The report tables are rebuilt from the stored metrics with:

```powershell
.\\.venv\\Scripts\\python.exe scripts\\build_task4_report.py
```

The evaluator verifies the frozen eval-set hash and writes the derived results under `evaluation/results/<run_id>/`. Compare each regenerated `metrics.json` with its frozen SHA-256 in [`TASK4_MANIFEST.json`](./TASK4_MANIFEST.json); any difference indicates the evaluation is not reproducible and must be investigated before relying on this report.
"""


def create_manifest() -> dict[str, Any]:
    paths = [
        "schemas/extraction_input.schema.json",
        "schemas/extraction_output.schema.json",
        "schemas/extraction_result.schema.json",
        "prompts/extraction/extraction_v2.0.md",
        "prompts/extraction/registry.json",
        "data/gold/quiz_gold_v1.0.json",
        "data/gold/organic_gold_v1.0.json",
        "data/gold/edge_cases_v1.0.json",
        "data/processed/eval_set_v1.json",
        "data/processed/split_v1.json",
        f"evaluation/runs/{DEV_ID}/manifest.json",
        f"evaluation/runs/{DEV_ID}/raw_responses.jsonl",
        f"evaluation/runs/{DEV_ID}/attempts.log.jsonl",
        f"evaluation/results/{DEV_ID}/metrics.json",
        f"evaluation/runs/{HELDOUT_ID}/manifest.json",
        f"evaluation/runs/{HELDOUT_ID}/raw_responses.jsonl",
        f"evaluation/runs/{HELDOUT_ID}/attempts.log.jsonl",
        f"evaluation/results/{HELDOUT_ID}/metrics.json",
    ]
    return {
        "version": "1.0",
        "hash_algorithm": "SHA-256",
        "frozen_prompt_version": "v2.0",
        "frozen_prompt_status": "frozen",
        "contract_version": "v1.0",
        "artifacts": {
            relative: sha256(ROOT / relative) for relative in paths
        },
    }


def main() -> None:
    validate_frozen_status()
    dev, dev_manifest = load_run(DEV_ID)
    heldout, heldout_manifest = load_run(HELDOUT_ID)
    candidate, _ = load_run(CANDIDATE_ID, expected_prompt_sha256=None)
    if candidate["run"]["prompt_version"] != "v2.1":
        raise ValueError("The dev comparison run is not the expected v2.1 candidate")
    if dev["response_count"] != len(raw_records(DEV_ID)):
        raise ValueError("Dev metrics do not cover every saved response")
    if heldout["response_count"] != len(raw_records(HELDOUT_ID)):
        raise ValueError("Held-out metrics do not cover every saved response")

    report = create_report(dev, dev_manifest, heldout, heldout_manifest, candidate)
    (TASK_DIR / "06_evaluation_report.md").write_text(report, encoding="utf-8")
    manifest = create_manifest()
    (TASK_DIR / "TASK4_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
