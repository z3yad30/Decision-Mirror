# Task 4.5 — Evaluation report

**Report generated:** 2026-10-28  
**Decision:** Ready with conditions  
**Frozen prompt:** v2.0

## 1. Purpose and scope

Task 4 implements and evaluates extraction of structured, evidence-supported T01–T06 traits from onboarding-quiz answers and organic decision narratives. It covers frozen input/output contracts, prompt versioning, a resumable inference runner, offline strict validation, gold-linked evaluation, error analysis, and a handoff contract for downstream profile aggregation. It does **not** establish clinical validity, population-level generalization, calibrated confidence, longitudinal self-consistency, or production fitness.

## 2. Datasets used

| Dataset | Records | Split | SHA-256 |
|---|---:|---|---|
| Quiz gold v1.0 | 125 | 75 dev / 50 held-out | `fc0c39a69da072c532a8abe54d5cfddfee6d0437dbe7ab16d41ed9fc7fafaba8` |
| Organic gold v1.0 | 20 | 14 dev / 6 held-out | `c071a2b3da5bf68f2c5edf28d83e7638aaa705d9bb768db32fd61b05991951e6` |
| Self-authored edge cases v1.0 | 11 | 11 dev / 0 held-out | `27f94d88fba1063302251fdc0651b4b0938a4190ee3e8ecac4e330b098d83919` |
| Unified evaluation set v1 | 156 | 100 dev / 56 held-out evaluated | `5825600d6a1962ccb94d288569894d72f9c5e2c440e5ba4fe2bab67650aa31b3` |
| Frozen split v1 | — | seed 42 | `3571248fb4a011dddc84f81de7bf13062e49b8528a2c7196a5dd24c4ee50b1c5` |

Quiz: independently sample 2 of each trait's 5 question IDs using random.Random(42), then assign every answer record for each question together. Organic: sample 2 records with an ontology §10 edge-case reference and 4 without using random.Random(42). Edge set: all records are dev.

This fixed split is used to reserve held-out examples from prompt iteration. Quiz options from one question stay together to avoid answer-option leakage; organic held-out records include both ontology edge-case-linked and other records; all self-authored edge records remain dev-only.

## 3. Experimental setup

| Setting | Value |
|---|---|
| Provider | Groq |
| Model | `openai/gpt-oss-120b` |
| Temperature | 0.0 |
| Reasoning effort | `medium` |
| Maximum completion tokens | 4096 |
| Prompt version | `v2.0` (registry status: frozen) |
| Prompt SHA-256 | `6f93b33da4bf2193641bb47156b1ca090a84f86f718e69085513aae4e6d280d7` |
| Contract version | v1.0 (input and output contracts frozen) |
| Evaluation-set SHA-256 | `5825600d6a1962ccb94d288569894d72f9c5e2c440e5ba4fe2bab67650aa31b3` |
| Dev run ID / date | `v2.0__openai-gpt-oss-120b__all-dev__5825600d` / 2026-10-26 |
| Held-out run ID / date | `v2.0__openai-gpt-oss-120b__all-heldout__5825600d` / 2026-10-28 |
| Run count | One logical run per split; 10 dev and 6 held-out API batches; 100 and 56 responses |
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

| Trait | Dev paired / target N | Dev non-null | Dev MAE [95% CI] | Dev exact band [95% CI] | Dev within 1 band | Dev QWK | Dev Spearman [95% CI] | Dev direction | Dev inversions | Held-out paired / target N | Held-out non-null | Held-out MAE [95% CI] | Held-out exact band [95% CI] | Held-out within 1 band | Held-out QWK | Held-out Spearman [95% CI] | Held-out direction | Held-out inversions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | 14 / 15 | 93.3% | 0.100 [0.046, 0.146] | 50.0% [28.6%, 78.6%] | 100.0% | 0.829 | 0.950 [0.841, 0.993] | 100.0% | 0 | 9 / 10 | 90.0% | 0.063 [0.011, 0.118] | 66.7% [33.3%, 100.0%] | 100.0% | 0.867 | 0.979 [0.872, 1.000] | 100.0% | 0 |
| T02 | 15 / 15 | 100.0% | 0.069 [0.025, 0.119] | 66.7% [40.0%, 86.7%] | 100.0% | 0.889 | 0.957 [0.873, 0.992] | 100.0% | 0 | 9 / 10 | 90.0% | 0.063 [0.007, 0.122] | 66.7% [33.3%, 100.0%] | 100.0% | 0.903 | 0.960 [0.777, 1.000] | 100.0% | 0 |
| T03 | 15 / 15 | 100.0% | 0.043 [0.020, 0.077] | 86.7% [66.7%, 100.0%] | 100.0% | 0.967 | 0.972 [0.914, 0.996] | 100.0% | 0 | 9 / 10 | 90.0% | 0.052 [0.004, 0.113] | 77.8% [44.4%, 100.0%] | 100.0% | 0.950 | 0.902 [0.534, 1.000] | 100.0% | 0 |
| T04 | 14 / 15 | 93.3% | 0.107 [0.057, 0.157] | 50.0% [21.4%, 78.6%] | 100.0% | 0.851 | 0.838 [0.586, 0.921] | 100.0% | 0 | 9 / 10 | 90.0% | 0.128 [0.061, 0.178] | 33.3% [11.1%, 66.7%] | 100.0% | 0.784 | 0.853 [0.579, 0.962] | 100.0% | 0 |
| T05 | 15 / 15 | 100.0% | 0.049 [0.017, 0.087] | 80.0% [60.0%, 100.0%] | 100.0% | 0.952 | 0.944 [0.813, 0.992] | 100.0% | 0 | 10 / 10 | 100.0% | 0.042 [0.005, 0.086] | 80.0% [50.0%, 100.0%] | 100.0% | 0.941 | 0.975 [0.877, 1.000] | 100.0% | 0 |
| overall | 73 / 75 | 97.3% | 0.073 [0.053, 0.094] | 67.1% [56.2%, 78.1%] | 100.0% | 0.906 | 0.918 [0.873, 0.947] | 100.0% | 0 | 46 / 50 | 92.0% | 0.069 [0.044, 0.094] | 65.2% [52.2%, 78.3%] | 100.0% | 0.898 | 0.927 [0.861, 0.964] | 100.0% | 0 |

### Organic results, v2.0

Per-trait numeric score agreement (paired non-null gold/model scores):

| Trait | Dev paired N | Dev MAE [95% CI] | Dev exact band [95% CI] | Dev within 1 band | Dev QWK | Dev Spearman [95% CI] | Dev direction | Held-out paired N | Held-out MAE [95% CI] | Held-out exact band [95% CI] | Held-out within 1 band | Held-out QWK | Held-out Spearman [95% CI] | Held-out direction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | 2 | 0.065 [0.050, 0.080] | 100.0% [100.0%, 100.0%] | 100.0% | 1.000 | 1.000 [1.000, 1.000] | 100.0% | 3 | 0.067 [0.000, 0.150] | 66.7% [0.0%, 100.0%] | 100.0% | 0.870 | 0.866 [0.866, 1.000] | 100.0% |
| T02 | 3 | 0.207 [0.020, 0.450] | 33.3% [0.0%, 100.0%] | 66.7% | 0.167 | 0.500 [-1.000, 1.000] | 66.7% | 3 | 0.083 [0.000, 0.150] | 33.3% [0.0%, 100.0%] | 100.0% | 0.667 | 1.000 [1.000, 1.000] | 100.0% |
| T03 | 5 | 0.044 [0.018, 0.074] | 40.0% [0.0%, 80.0%] | 100.0% | 0.848 | 0.803 [0.395, 1.000] | 100.0% | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] | n/a | n/a | n/a [n/a, n/a] | n/a |
| T04 | 2 | 0.200 [0.200, 0.200] | 0.0% [0.0%, 0.0%] | 100.0% | 0.800 | 1.000 [1.000, 1.000] | 100.0% | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] | n/a | n/a | n/a [n/a, n/a] | n/a |
| T05 | 3 | 0.067 [0.000, 0.150] | 66.7% [0.0%, 100.0%] | 100.0% | 0.941 | 0.866 [0.866, 1.000] | 100.0% | 1 | 0.100 [0.100, 0.100] | 100.0% [100.0%, 100.0%] | 100.0% | 1.000 | n/a [n/a, n/a] | 100.0% |
| overall | 15 | 0.105 [0.053, 0.170] | 46.7% [20.0%, 73.3%] | 93.3% | 0.788 | 0.775 [0.425, 0.930] | 93.3% | 7 | 0.079 [0.036, 0.121] | 57.1% [14.3%, 85.7%] | 100.0% | 0.784 | 0.914 [0.661, 1.000] | 100.0% |

Pooled organic diagnostics and factor results:

| Organic metric | Dev | Held-out |
|---|---:|---:|
| Paired numeric scores | 15 | 7 |
| MAE [95% CI] | 0.105 [0.053, 0.170] | 0.079 [0.036, 0.121] |
| Exact band accuracy [95% CI] | 46.7% [20.0%, 73.3%] | 57.1% [14.3%, 85.7%] |
| Missed-signal rate | 11.8% | 0.0% |
| Unsupported-inference rate | 15.4% | 7.1% |
| Status accuracy | 100.0% | 100.0% |
| Confidence MAE | 0.177 | 0.077 |
| Evidence token-overlap F1 (report-only) | 0.261 | 0.227 |
| Situational-factor precision | 60.0% (TP 3, FP 2, FN 0) | 50.0% (TP 1, FP 1, FN 0) |
| Situational-factor recall | 100.0% (TP 3, FP 2, FN 0) | 100.0% (TP 1, FP 1, FN 0) |
| Situational-factor category agreement | 0.0% (TP 3, FP 2, FN 0) | 100.0% (TP 1, FP 1, FN 0) |

The organic held-out set contains only 6 records. Its estimates—including situational-factor recall (100.0%)—are **not statistically meaningful** and must not be interpreted as stable rates.

### Prompt-version progression on dev only

| Dev metric | v2.0 frozen baseline | v2.1 rejected candidate |
|---|---:|---:|
| Quiz exact-band accuracy | 67.1% | 73.2% |
| Quiz MAE | 0.073 | 0.064 |
| Quiz Spearman rho | 0.918 | 0.916 |
| Organic situational-factor recall | 100.0% | 66.7% |
| Organic situational-factor precision | 60.0% | 50.0% |
| Organic factor category agreement | 0.0% | 0.0% |
| Edge-case checks | 39/47 (83.0%) | 40/47 (85.1%) |

v2.1 is rejected, not a final prompt: as documented in [`05_error_analysis.md`](./05_error_analysis.md), its clarifying change reduced eligible organic situational-factor recall below the registered threshold by missing ORG11. Despite better quiz and edge metrics, v2.1 is retained only as a draft. The official final evaluated pair is v2.0 dev and v2.0 held-out.

### Ambiguous gold, separately reported

These items are excluded from headline organic metrics. The per-trait values below are calculated from the evaluator's `ambiguous_gold_score_metrics`; they are not pooled with the headline results.

| Split | Item IDs (`ambiguous_gold`) | Trait | Paired N | MAE | Exact band |
|---|---|---|---:|---:|---:|
| Dev | ORG05, ORG10, ORG15, ORG18 | T01 | 2 | 0.050 | 100.0% |
| Dev | ORG05, ORG10, ORG15, ORG18 | T02 | 1 | 0.100 | 100.0% |
| Dev | ORG05, ORG10, ORG15, ORG18 | T03 | 0 | n/a | n/a |
| Dev | ORG05, ORG10, ORG15, ORG18 | T04 | 0 | n/a | n/a |
| Dev | ORG05, ORG10, ORG15, ORG18 | T05 | 1 | 0.050 | 100.0% |
| Dev | ORG05, ORG10, ORG15, ORG18 | overall | 4 | 0.062 | 100.0% |
| Held-out | ORG04, ORG19 | T01 | 0 | n/a | n/a |
| Held-out | ORG04, ORG19 | T02 | 0 | n/a | n/a |
| Held-out | ORG04, ORG19 | T03 | 0 | n/a | n/a |
| Held-out | ORG04, ORG19 | T04 | 0 | n/a | n/a |
| Held-out | ORG04, ORG19 | T05 | 0 | n/a | n/a |
| Held-out | ORG04, ORG19 | overall | 0 | n/a | n/a |

Dev ambiguous item IDs: ORG05, ORG10, ORG15, ORG18. Held-out ambiguous item IDs: ORG04, ORG19.

## 7. Pre-registered criteria

The thresholds remain proposed and pending team-lead approval, as stated in the evaluation method. Criterion observations and pass/fail statuses below are read from the two final v2.0 `metrics.json` files; `not_applicable` is not counted as a pass.

| Criterion | Threshold | Dev | Held-out | Dev result | Held-out result |
|---|---:|---:|---:|---|---|
| Strict schema-valid rate | ≥ 95.0% | 100.0% | 100.0% | pass | pass |
| Schema-valid or recovered diagnostic rate | ≥ 99.0% | 100.0% | 100.0% | pass | pass |
| Quiz target non-null rate | ≥ 90.0% | 97.3% | 92.0% | pass | pass |
| Quiz exact-band accuracy | ≥ 60.0% | 67.1% | 65.2% | pass | pass |
| Quiz within-one-band rate | ≥ 90.0% | 100.0% | 100.0% | pass | pass |
| Quiz MAE | ≤ 0.150 | 0.073 | 0.069 | pass | pass |
| Quiz direction accuracy | ≥ 90.0% | 100.0% | 100.0% | pass | pass |
| Quiz Spearman rho | ≥ 0.800 | 0.918 | 0.927 | pass | pass |
| Quiz polarity-inversion rate | ≤ 2.0% | 0.0% | 0.0% | pass | pass |
| Evidence grounding | ≥ 98.0% | 100.0% | 100.0% | pass | pass |
| T06 violations | = 0 | 0 | 0 | pass | pass |
| Edge-case pass rate | ≥ 80.0% | 83.0% | n/a | pass | not_applicable |
| Organic situational-factor recall | ≥ 80.0% | 100.0% | 100.0% | pass | pass |

## 8. Representative correct and incorrect cases and edge-case results

The following input, gold, and model-output blocks are reproduced from the frozen eval set and the saved runs' raw `response_text` values. The correct case means correct by score band only; evidence quality still needs human review.

### Correct by target score band: Q02_B

The target-trait prediction is in the same score band as its numeric quiz gold. This is score agreement, not independent evidence-quality adjudication.

**Raw input (`decision_text`):**

```text
Scenario: You have savings that could support you for several months. You can either keep them in a predictable low-return account or use part of them for a business idea with a meaningful chance of failure.
Selected answer: I would invest only a small amount because I strongly prefer protecting the savings.
```

**Gold annotation:**

```json
{
  "target_trait": "T01",
  "traits": {
    "T01": {
      "value": 0.3,
      "confidence": 0.7
    },
    "T02": null,
    "T03": null,
    "T04": null,
    "T05": null,
    "T06": null
  },
  "situational_factor": null,
  "ambiguous_gold": false
}
```

**Raw model output (`response_text`):**

```json
{"decision_id":"Q02_B","extraction_status":"success","traits":[{"trait_id":"T01","trait_name":"Risk Tolerance","score":0.3,"confidence":0.65,"evidence":["I would invest only a small amount because I strongly prefer protecting the savings."],"situational_factor":{"category":"financial_dependency","description":"Savings limited to several months of support"},"context_notes":"Preference for protecting savings over a risky business idea indicates a risk‑averse stance; confidence moderate due to implied trade‑off."},{"trait_id":"T02","trait_name":"Time Horizon","score":null,"confidence":0.0,"evidence":[],"situational_factor":null,"context_notes":"No supported evidence for this trait."},{"trait_id":"T03","trait_name":"Locus of Priority","score":null,"confidence":0.0,"evidence":[],"situational_factor":null,"context_notes":"No supported evidence for this trait."},{"trait_id":"T04","trait_name":"Decisiveness Speed","score":null,"confidence":0.0,"evidence":[],"situational_factor":null,"context_notes":"No supported evidence for this trait."},{"trait_id":"T05","trait_name":"Emotional vs. Analytical Weighting","score":0.1,"confidence":0.55,"evidence":["I would invest only a small amount because I strongly prefer protecting the savings."],"situational_factor":{"category":"financial_dependency","description":"Savings limited to several months of support"},"context_notes":"Decision is based on personal preference rather than analytical reasoning, indicating emotional weighting."},{"trait_id":"T06","trait_name":"Self-Consistency","score":null,"confidence":0.0,"evidence":[],"situational_factor":null,"context_notes":"History is unavailable in this task."}]}
```

### Incorrect case: EDGE03

The dev-only self-authored expectation required all traits null, a situational factor, and low confidence. The recorded output incorrectly scored T05 from a budget constraint.

**Raw input (`decision_text`):**

```text
I accepted the only apartment I could afford because the other available places were outside my budget; I had no realistic alternative.
```

**Gold annotation:**

```json
{
  "traits": {
    "T01": null,
    "T02": null,
    "T03": null,
    "T04": null,
    "T05": null,
    "T06": null
  },
  "situational_factor": null,
  "ambiguous_gold": false,
  "expected": {
    "expect_status": "insufficient_evidence",
    "expect_null_traits": [
      "T01",
      "T02",
      "T03",
      "T04",
      "T05",
      "T06"
    ],
    "expect_non_null_traits": [],
    "expect_situational_factor": true,
    "max_confidence": 0.2
  }
}
```

**Raw model output (`response_text`):**

```json
{
  "decision_id": "EDGE03",
  "extraction_status": "success",
  "traits": [
    {
      "trait_id": "T01",
      "trait_name": "Risk Tolerance",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No supported evidence for this trait."
    },
    {
      "trait_id": "T02",
      "trait_name": "Time Horizon",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No supported evidence for this trait."
    },
    {
      "trait_id": "T03",
      "trait_name": "Locus of Priority",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No supported evidence for this trait."
    },
    {
      "trait_id": "T04",
      "trait_name": "Decisiveness Speed",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No supported evidence for this trait."
    },
    {
      "trait_id": "T05",
      "trait_name": "Emotional vs. Analytical Weighting",
      "score": 0.7,
      "confidence": 0.6,
      "evidence": [
        "I accepted the only apartment I could afford because the other available places were outside my budget; I had no realistic alternative."
      ],
      "situational_factor": {
        "category": "external_constraint",
        "description": "Only affordable apartment due to budget; no realistic alternative."
      },
      "context_notes": "Decision is based on budget limitation, an external financial constraint, which provides moderate analytical reasoning evidence but reduces confidence."
    },
    {
      "trait_id": "T06",
      "trait_name": "Self-Consistency",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "History is unavailable in this task."
    }
  ]
}
```

### Incorrect case: Q01_A

Held-out quiz target T01 has a numeric gold score, but the model returned null (missed signal and status error).

**Raw input (`decision_text`):**

```text
Scenario: You receive two job offers. Offer A is stable and pays $1,500/month. Offer B pays $1,000/month now but could grow substantially if the company succeeds.
Selected answer: I would choose the stable $1,500 offer.
```

**Gold annotation:**

```json
{
  "target_trait": "T01",
  "traits": {
    "T01": {
      "value": 0.1,
      "confidence": 0.7
    },
    "T02": null,
    "T03": null,
    "T04": null,
    "T05": null,
    "T06": null
  },
  "situational_factor": null,
  "ambiguous_gold": false
}
```

**Raw model output (`response_text`):**

```json
{
  "decision_id": "Q01_A",
  "extraction_status": "insufficient_evidence",
  "traits": [
    {
      "trait_id": "T01",
      "trait_name": "Risk Tolerance",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No explicit reasoning about uncertainty or trade‑off is provided; the answer only states a choice, which is insufficient evidence."
    },
    {
      "trait_id": "T02",
      "trait_name": "Time Horizon",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No stated consideration of near‑term versus long‑term outcomes; the answer merely selects an option, providing insufficient evidence."
    },
    {
      "trait_id": "T03",
      "trait_name": "Locus of Priority",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No other party or external interest is mentioned; insufficient evidence to assess priority locus."
    },
    {
      "trait_id": "T04",
      "trait_name": "Decisiveness Speed",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "No information about deliberation time or decision speed is provided."
    },
    {
      "trait_id": "T05",
      "trait_name": "Emotional vs. Analytical Weighting",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "The answer contains no explicit emotional or analytical reasoning; evidence is insufficient."
    },
    {
      "trait_id": "T06",
      "trait_name": "Self-Consistency",
      "score": null,
      "confidence": 0.0,
      "evidence": [],
      "situational_factor": null,
      "context_notes": "History is unavailable in this task."
    }
  ]
}
```

### Edge-case results

| Split | Checks passed | Checks total | Pass rate | Failed items |
|---|---:|---:|---:|---|
| Dev | 39 | 47 | 83.0% | EDGE03, EDGE04, EDGE06, EDGE09 |
| Held-out | 0 | 0 | n/a | No edge records in held-out split |

Edge cases exist **only in the dev split** and are self-authored. The held-out split has no edge cases, so the edge pass rate has no held-out counterpart.

## 9. Error categories

Counts are error-log rows; a single item may contribute multiple rows. `needs_manual_review` is a reviewer flag, not an automated error finding.

| Error category | Dev count | Held-out count | Meaning |
|---|---:|---:|---|
| `malformed_output` | 0 | 0 | Empty/non-JSON output or schema/semantic validation failure. |
| `missed_signal` | 4 | 4 | A gold-supported organic or quiz target trait was returned null. |
| `unsupported_inference` | 6 | 1 | A score was emitted for a gold-null organic trait. |
| `polarity_inversion` | 1 | 0 | Prediction is on the opposite side of 0.5 by more than 0.2. |
| `score_deviation` | 32 | 19 | Paired numeric score differs by one or more score bands. |
| `evidence_not_grounded` | 0 | 0 | Evidence quote was not found in normalized input text. |
| `context_confusion` | 5 | 1 | Situational factor is missed, hallucinated, miscategorized, or a constraint is scored as a trait. |
| `confidence_miscalibration` | 1 | 0 | Confidence is at least 0.8 with an error of two or more bands. |
| `status_error` | 1 | 1 | Output status differs from status implied by the gold. |
| `t06_violation` | 0 | 0 | T06 is non-null without supplied history. |
| `edge_case_failure` | 8 | 0 | A qualitative edge expectation check failed. |
| `needs_manual_review` | 10 | 10 | Deterministic cross-review flag; not an automated finding. |

The main observed failure patterns are score compression toward interior bands, unsupported trait scoring, and confusion between situational circumstances and stable traits. Situational-factor category agreement is weak even where the binary factor-presence metric passes; see the dev error analysis for item-level diagnoses.

## 10. Limitations

- These results use one model from one provider (`openai/gpt-oss-120b` on Groq). The team's earlier ChatGPT tests are not comparable because the model/provider and evaluation conditions differ.
- Quiz gold confidence is uniformly 0.70 and the source has a documented 0.70/0.90 inconsistency; confidence agreement is not a strong calibration claim. Quiz evidence is templated.
- There are only 20 organic gold items, with 6 held out; organic held-out metrics, including situational-factor recall, have very wide uncertainty and are not statistically meaningful.
- Edge cases are self-authored qualitative expectations and exist only in dev.
- Organic dev metrics were visible during prompt iteration; the v2.1 candidate was rejected on dev evidence. Held-out results were reserved for evaluation of the selected v2.0 prompt, not used for prompt revisions.
- Free-tier quota and rate-limit constraints limited the practical number and timing of API runs.
- Evaluation language(s): en. English only.
- Quiz answers are much easier and shorter than real narratives, so quiz performance likely overstates real-world accuracy.
- Gold annotations have known ambiguities. `ORG14` gold assigns T06=0.85, but T06 is excluded from score comparison because the contract requires null without supplied history; the model's null is contract-compliant.
- Strict schema validity and grounded quotations do not prove that the interpretation is correct. The dev run contains 10 deterministic manual-review flags, and human evidence cross-review remains outstanding.

## 11. Readiness decision

**Decision: Ready with conditions** for a limited, guarded downstream profile-aggregation pilot—not for unsupervised or high-impact use.

All applicable pre-registered numeric criteria pass on the final v2.0 dev and held-out runs. This is a positive engineering readiness signal, not validation. Conditions are: (1) team-lead approval of the proposed thresholds and this report; (2) human cross-review of evidence support before trusting aggregated profiles; (3) do not treat confidence as calibrated probability; (4) keep T06 null until longitudinal history is supplied under a later contract; and (5) preserve the situational-factor down-weighting and known-failure safeguards in the handoff. Organic held-out and edge-case evidence is too small to support an unconditional readiness claim.

**Approval:** ______________________________ (name)  **Date:** __________________

## 12. Reproduction steps

From a fresh clone on Windows PowerShell, use the project's pinned environment and the saved runs. These commands do not call the API. Using the venv's Python executable directly avoids PowerShell script-execution-policy differences:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-dev__5825600d
.\.venv\Scripts\python.exe scripts\evaluate_run.py --run-id v2.0__openai-gpt-oss-120b__all-heldout__5825600d
```

The report tables are rebuilt from the stored metrics with:

```powershell
.\.venv\Scripts\python.exe scripts\build_task4_report.py
```

The evaluator verifies the frozen eval-set hash and writes the derived results under `evaluation/results/<run_id>/`. Compare each regenerated `metrics.json` with its frozen SHA-256 in [`TASK4_MANIFEST.json`](./TASK4_MANIFEST.json); any difference indicates the evaluation is not reproducible and must be investigated before relying on this report.
