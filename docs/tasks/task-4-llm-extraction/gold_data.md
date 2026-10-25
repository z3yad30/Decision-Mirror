# Task 4 evaluation data

## Dataset inventory

- [`quiz_gold_v1.0.json`](../../../data/gold/quiz_gold_v1.0.json) contains the
  existing 125 onboarding-quiz answer records: 25 questions, five answer
  choices per question, and one target trait per record.
- [`organic_gold_v1.0.json`](../../../data/gold/organic_gold_v1.0.json)
  transcribes the 20 annotated decision narratives in Ontology §9. Its
  `gold_traits` keys are T01–T06; an object with `value: null` and non-zero
  confidence faithfully preserves a dashed ontology value without inventing a
  score.
- [`edge_cases_v1.0.json`](../../../data/gold/edge_cases_v1.0.json) contains
  11 self-authored inputs with qualitative expected behavior checks. These
  checks are not numeric gold labels.
- [`split_v1.json`](../../../data/processed/split_v1.json) records the fixed
  seed-42 development/holdout assignments.
- [`eval_set_v1.json`](../../../data/processed/eval_set_v1.json) is the
  unified, schema-valid extraction-input collection.
- [`MANIFEST.json`](../../../data/processed/MANIFEST.json) records SHA-256
  hashes for each gold file, the split, and the generated evaluation set.

Rebuild the unified file and manifest from the gold files and frozen split:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/build_eval_set.py
```

The builder uses the existing `build_quiz_payload` implementation and emits
JSON deterministically. It never puts quiz labels, evidence, answer-option
lists, or other gold fields in a payload. After an API run begins, do not
regenerate or edit `split_v1.json`.

## Provenance and annotation policy

Quiz gold is the supplied Task 3 dataset. The organic set was transcribed from
`docs/ontology/Decision_Mirror_Trait_Ontology_Complete.pdf`, §9, using
`pdftotext -layout`; decision narratives and annotation wording are retained
as printed. Situational-factor descriptions preserve the ontology's wording;
the `category` field maps it to the extraction-output schema's permitted
categories. Explicit ontology `--` values remain null and retain their stated
confidence. The `ambiguous_gold` flag and note expose, rather than resolve,
uncertainty in the source annotation.
Category mapping is conservative: for example, a caregiving context explicitly
framed as a value is mapped to `other`, not `family_pressure`, while a stated
hard limitation is mapped to `external_constraint`.

The edge set is self-authored for testing. It includes insufficient inputs,
constraints, conflicting motivations, emotional and analytical cues,
contradiction, multiple traits, unsupported history claims, a long narrative
with a single relevant decision signal, and two embedded instruction-injection
attempts. All edge cases are development data and use behavior expectations
instead of numeric target scores.

## Split rule and purpose

For quiz data, two of each trait's five questions are held out (10 questions,
50 records); all five answers for a question remain together. The other 15
questions (75 records) are development data. For organic data, six of 20
records are held out, including at least two items linked to an ontology §10
edge case. All self-authored edge data remains development-only. The split is
seeded with 42 and its exact IDs are stored rather than sampled at evaluation
time.

The holdout exists to measure prompt behavior on examples not used during
development and to reduce prompt overfitting. Do not use held-out results to
iterate on prompts; report them separately from development results.

## Dataset limits

- The organic set is tiny (20 decisions) and cannot establish broad
  generalization.
- Quiz confidence is uniformly 0.70 and the source itself notes a 0.70/0.90
  inconsistency elsewhere in its source material; confidence agreement should
  not be treated as a strong calibration measure.
- Quiz evidence is templated and single-trait; evidence quality should be
  assessed for grounding, not exact string agreement.
- Organic evidence sometimes consists of annotation rationale rather than a
  literal quote. Preserve it as transcribed; do not interpret it as a source
  quote from the narrative.
- Organic items ORG04 and ORG05 retain dashed values with non-zero confidence.
  Other items explicitly marked ambiguous/edge-case in the ontology are also
  flagged and should be reported separately.
- The edge cases are self-authored and qualitative; their expectations are
  behavioral checks, not a validated annotation benchmark.
- T06 is longitudinal in meaning. A claim such as “I always do this” without
  supplied history does not satisfy the input contract's history requirement.

## KNOWN_ISSUES

1. Quiz confidence is uniformly 0.70 although the source documents describe a
   0.90 example; the team has not resolved the discrepancy.
2. Ontology Decisions 4 and 5 use `--` where a numeric value might otherwise
   be expected, while retaining non-zero confidence. Their score remains null
   in this dataset.
3. The ontology's case labels can describe a case as ambiguous even when it
   assigns some numeric traits. These records are flagged for separate
   analysis without altering their annotations.
4. The organic sample, quiz calibration labels, and self-authored edge set are
   not clinically validated and do not justify population-level claims.
5. **Nothing in gold was changed.** The supplied quiz gold was not edited; the
   organic data is a transcription, and the edge data is a separate
   self-authored behavioral test set.
