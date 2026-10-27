# Task 4.4–4.5 Evaluation Method

**Status of readiness thresholds: proposed — pending team lead approval.**
These thresholds are preregistered here; do not change them after inspecting
run results. The evaluator is offline and never modifies `raw_responses.jsonl`.
It joins each raw record to the frozen `eval_set_v1.json` by `item_id`, uses
the matching gold annotation, and validates `response_text` with the strict
Prompt 2 validator. A response with a diagnostic `recovered` candidate remains
invalid; recovered text is never substituted for the original response.

The Task 4 assignment's sections 4.4 and 4.5 require comparisons against human
annotations, retained disagreements, reproducible experimental details, result
tables, representative difficult cases, error categories, limitations, and a
readiness decision for downstream aggregation. This method implements those
deliverables without correcting either model output or gold data.

## Reproduce the evaluation

Activate `.venv`, then run against a completed or partial run identifier:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/evaluate_run.py --run-id <run_id>
python scripts/compare_runs.py <run_a> <run_b>
```

The first command reads `evaluation/runs/<run_id>/raw_responses.jsonl`, its
manifest, the frozen evaluation set, and the gold annotations; it makes no API
calls. It refuses an evaluation-set hash mismatch and writes:
`metrics.json`, `per_item.csv`, `error_log.jsonl`, `schema_compliance.json`,
`tables.md`, and `difficult_cases.md` under
`evaluation/results/<run_id>/`. The second command first evaluates both runs
and writes a paired common-item score comparison under
`evaluation/comparisons/`. Null-to-score transitions are counted separately
from numeric score deltas.

Partial runs are evaluated only on records present in their raw JSONL file.
Missing items are not treated as model outputs; quiz non-null rates use target
items actually present, while score agreement denominators use items with both
a gold numeric score and a model numeric score. Misses are independently
reported as missed signals. Quiz off-target scores are a separate diagnostic
and never enter headline quiz score metrics.

## Score bands and numeric metrics

There are five half-open score bands, except that the last includes 1.0:

| Band index | Interval | Gold anchors at band centers |
|---:|---|---|
| 0 | `[0.0, 0.2)` | 0.1 |
| 1 | `[0.2, 0.4)` | 0.3 |
| 2 | `[0.4, 0.6)` | 0.5 |
| 3 | `[0.6, 0.8)` | 0.7 |
| 4 | `[0.8, 1.0]` | 0.9 |

For a set of `n` paired numeric scores `(g_i, p_i)`, where `g` is gold and `p`
is the model score:

- **MAE** = `sum(abs(g_i - p_i)) / n`.
- **Exact band accuracy** = count(`band(g_i) == band(p_i)`) / `n`.
- **Within-one-band rate** = count(`abs(band(g_i) - band(p_i)) <= 1`) / `n`.
- **Quadratic-weighted Cohen's κ** = `1 - observed_weighted_disagreement /
  expected_weighted_disagreement`; cell weight is `(i-j)^2 / 16` on the 5×5
  band confusion matrix. It is 1 for perfect agreement and undefined when
  expected disagreement is zero but observed disagreement is nonzero.
- **Spearman ρ** is Pearson correlation of average ranks (ties receive average
  ranks); it is undefined for fewer than two pairs or a constant rank vector.
- **Direction accuracy** compares `< 0.5` versus `> 0.5`, excluding gold
  exactly 0.5. A predicted 0.5 is on the lower side for this binary comparison.
- **Polarity inversion** is an opposite-side prediction whose absolute score
  difference is strictly greater than 0.2. The rate denominator is all paired
  numeric scores; counts are also reported for each trait, particularly T03
  and T05.
- The **5×5 confusion matrix** rows are gold bands and columns are predicted
  bands, in the order shown above.

Each metric is reported for quiz target traits T01–T05 and the pooled overall
target set. The target-trait non-null rate is the number of selected quiz
records with a non-null model target score divided by selected target records.
For numeric agreement, only gold-non-null/model-non-null pairs enter the score
formulas; target non-null coverage and missed signals are reported separately.
For each quiz trait and overall, 95% percentile bootstrap intervals are
reported for MAE, exact band accuracy, and Spearman ρ. The bootstrap samples
paired records with replacement, uses 2,000 replicates and seed 42, and takes
the empirical 2.5th and 97.5th percentiles. Undefined replicate correlations
are omitted; the number of valid replicates is recorded.

Quiz off-target extraction is the number of non-target T01–T05 scores that are
non-null divided by the five non-target opportunities per selected quiz item.
Its grounded-evidence share is the number of those predictions with at least
one evidence quote and all evidence quotes grounded, divided by off-target
predictions. These values are reported separately and are not treated as
headline scoring errors. Quiz gold evidence is templated, so it is never
text-matched to model evidence.

For organic decisions, score metrics use gold-non-null traits T01–T05 and the
same formulas. Numeric agreement uses paired non-null scores. **Missed-signal
rate** is gold-non-null traits predicted null divided by all gold-non-null
traits. **Unsupported-inference rate** is non-null predictions on gold-null
T01–T05 traits divided by all gold-null T01–T05 opportunities. A T06 prediction
without history is tracked separately. `ambiguous_gold` records are excluded
from headline organic score, missed/unsupported inference, status,
factor-detection, and confidence metrics; their numeric score comparisons, if
available, are reported separately. Organic confidence MAE includes only
unambiguous gold-non-null traits with both model and gold confidence values.

Organic status accuracy compares output status with status derived from gold:
`success` iff any T01–T06 gold value is numeric, otherwise
`insufficient_evidence`. Situational-factor detection is binary per decision:
at least one predicted factor is a detection. Precision is `TP/(TP+FP)`;
recall is `TP/(TP+FN)`. Category agreement is the share of true detections
whose predicted categories include the gold category. Multiple predicted
categories count as a detection once.

## Evidence, confidence, edge cases

Evidence grounding is the fraction of all returned evidence quotes found in
their item's `decision_text` after normalizing whitespace, typographic quotes,
balanced surrounding quote delimiters, and case. Empty evidence contributes no
quote to the denominator. For organic items, token-overlap F1 compares all
predicted evidence to the transcribed `gold_evidence` using multiset token
overlap and is **report-only**: some gold evidence is annotation rationale
rather than a literal source quote. The templated quiz gold evidence is never
text-matched.

Confidence distribution counts confidence values for every non-null model
trait score. Mean confidence when band-correct or band-wrong is calculated on
paired numeric gold traits, with correctness meaning exact band agreement.
High-confidence-wrong means confidence `>= 0.8` and score error of at least
two bands; the rate denominator is all scored model trait confidences. Uniform
quiz gold confidence 0.70 is not treated as a confidence target. Organic
confidence MAE is reported only for the eligible unambiguous pairs described
above.

Each edge expectation is one check: expected status, all named null traits,
all named non-null traits, expected presence/absence of any situational factor,
and (when present) maximum confidence for expected non-null traits. The
edge-case pass rate is passed checks divided by all defined checks. Per-item
failures are listed; edge expectations are behavior checks, not numeric gold.

## Error taxonomy

`error_log.jsonl` has `item_id`, `expected`, `actual`, `error_type`, `severity`,
and `notes`. One item can have multiple error rows. Severity and assignment
rules:

| Error type | Rule | Severity |
|---|---|---|
| `malformed_output` | Empty/non-JSON output, schema violation, or semantic violation | Critical |
| `missed_signal` | Organic gold numeric trait is model null | Major |
| `unsupported_inference` | Organic T01–T05 gold null trait receives a score | Major |
| `polarity_inversion` | Wrong side of 0.5 by more than 0.2 | Critical |
| `score_deviation` | Difference of 1, 2, or at least 3 bands | Minor, major, or critical |
| `evidence_not_grounded` | Evidence quote not found in normalized decision text | Major |
| `context_confusion` | Situational factor missed/hallucinated/category mismatch, or an external constraint receives a trait score | Major |
| `confidence_miscalibration` | Confidence >= 0.8 with an error of at least 2 bands | Major |
| `status_error` | Output status differs from status derived from gold | Major |
| `t06_violation` | T06 non-null without supplied history | Major |
| `edge_case_failure` | One qualitative expected behavior check fails | Major |
| `needs_manual_review` | Deterministic sample of up to 10 exact-band-correct items for cross-review | Review |

`needs_manual_review` is a human task flag, not an automated finding that
evidence is incorrect. It samples correct-by-score items deterministically
(seed 42); a reviewer must decide whether the evidence really supports the
score. `schema_compliance.json` also reports strict parse, schema, semantic,
and lenient `recovered` results per item. Recovered text remains a malformed
output.

## Preregistered readiness criteria

The following are **proposed — pending team lead approval**. Results are
reported as pass/fail when the relevant data is present and not applicable
otherwise. A combined schema-valid-or-recovered rate counts each strict
schema-valid response plus each additional response flagged `recovered`; this
diagnostic does not mean the recovered response is valid or should be used.

| Criterion | Threshold |
|---|---:|
| Strict schema-valid rate | >= 95% |
| Schema-valid or recovered diagnostic rate | >= 99% |
| Quiz target non-null rate | >= 90% |
| Quiz exact band accuracy | >= 60% |
| Quiz within-one-band rate | >= 90% |
| Quiz MAE | <= 0.15 |
| Quiz direction accuracy | >= 90% |
| Quiz Spearman ρ | >= 0.80 |
| Quiz polarity-inversion rate | <= 2% |
| Evidence grounding | >= 98% |
| T06 violations | 0 |
| Edge-case pass rate | >= 80% |
| Organic situational-factor recall | >= 80% |

Quiz criteria apply to quiz records in the evaluated run. Evidence grounding
and T06 apply to all evaluated response records; edge and organic criteria
apply only when those sets are present. A missing denominator is reported as
not applicable, not as a pass. Passing these proposed thresholds is a
quantitative readiness signal only; the organic set is small, quiz labels have
known limitations, and human evidence cross-review remains necessary before a
downstream readiness decision.

## Limitations

The quiz contains one target trait per item and templated evidence; off-target
scores are reported rather than penalized. Organic gold has 20 items, including
ambiguous annotations, and is not representative of a general population.
Edge checks are self-authored qualitative expectations. These results are
research evaluation, not clinical or population-level validation. The final
decision for downstream profile aggregation remains a team-lead decision and
must consider the quantitative results, manual evidence review, and these
limitations.
