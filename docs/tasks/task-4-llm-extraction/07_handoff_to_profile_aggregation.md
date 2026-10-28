# Task 4 handoff to profile aggregation

## What this extraction stage guarantees

- **Contract:** Task 4 input and output contracts are frozen at v1.0. The output schema and semantic rules are in [`02_output_spec.md`](./02_output_spec.md).
- **Trait slots:** every response contains T01–T06 in the defined order. An unsupported trait is `score: null`, `confidence: 0.0`, and `evidence: []`; do not replace null with a midpoint or infer a score from another trait.
- **Status:** `success` means at least one trait has a non-null score. `insufficient_evidence` means all trait scores are null. Pipeline errors are not model outputs.
- **Provenance:** cite the frozen extraction prompt v2.0, SHA-256 `6f93b33da4bf2193641bb47156b1ca090a84f86f718e69085513aae4e6d280d7`, with model `openai/gpt-oss-120b` on Groq. The evaluated run IDs, configuration, and results are in [`06_evaluation_report.md`](./06_evaluation_report.md).

## Interpreting confidence

The per-trait `confidence` field describes the quality of the evidence for that score—its explicitness, relevance, and the effect of context or constraints. It is not confidence in the person's decision, a probability that the score is correct, or a calibrated probability. The quiz gold's uniform confidence value is not a calibration target. A null score must have confidence exactly `0.0`; its confidence must not be used to distinguish degrees of uncertainty.

Downstream aggregation may use confidence as a **relative evidence weight** only after defining and validating an explicit weighting policy. Do not treat confidence as calibrated probability or apply an assumed numeric transform. In particular, contextual factors should reduce the influence of an affected observation rather than become stable-trait evidence themselves.

## Situational factors and down-weighting

`situational_factor` records a decision-specific temporary circumstance or constraint separately from a trait. When one affects the evidence for a non-null trait, down-weight that observation in aggregation relative to an otherwise comparable observation without that influence. Keep the factor category and description available for review; do not convert the factor into a durable user attribute or treat the factor's presence as support for a trait. The contract does not prescribe a numeric down-weighting formula, so profile aggregation must document and validate its own policy before use.

An explicit preference can still be scored when supported by the narrative, even if a circumstance affects the decision; the context should lower the affected score's evidential weight, not erase or recast the stated preference automatically.

## T06 and longitudinal history

T06 (Self-Consistency) is **always null in Task 4** because no longitudinal history is supplied. The profile stage must not infer T06 from a single narrative or from a statement such as “I always do this.” Gold ORG14's T06 value is excluded from Task 4 score comparison because it conflicts with the contract's no-history rule. Supporting T06 requires a future input/contract change and repeated observations.

## Known weak traits and failure modes

- T04 (Decisiveness Speed) is comparatively weak on quiz exact-band results: it is the lowest trait in the held-out run and has wide uncertainty. Avoid treating its point estimate as stable.
- Predictions tend to compress extreme quiz gold values toward inner score bands.
- Organic dev results show unsupported trait scores, situational-factor false positives/category confusion, and constraints being misread as analytical evidence (for example, EDGE03).
- The v2.0 dev run's organic situational-factor category agreement is weak. The held-out estimate is based on only six organic records and is not statistically meaningful; neither set establishes robust factor categorization.
- Confidence may be overstated on conflicted narratives. The report's deterministic manual-review sample still requires human evidence-support review.
- Quiz items are short and templated. Their accuracy should not be transferred to real narratives; null behavior and evidence grounding do not by themselves establish interpretive correctness.

Use the full results, denominators, ambiguity handling, limitations, and conditional readiness decision in [`06_evaluation_report.md`](./06_evaluation_report.md). Task 4 supports only a guarded aggregation pilot with the conditions stated there; it does not authorize unsupervised high-impact use.
