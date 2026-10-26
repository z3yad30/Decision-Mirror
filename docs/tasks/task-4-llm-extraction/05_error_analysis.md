# Dev-split error analysis and prompt revision

## Scope and run

- Baseline run: `v2.0__openai-gpt-oss-120b__all-dev__5825600d`
- Prompt: `v2.0` (`6f93b33d…`)
- Model: `openai/gpt-oss-120b`; 100 responses; dev split only (75 quiz, 14
  organic, 11 edge cases)
- Evaluation: `evaluation/results/v2.0__openai-gpt-oss-120b__all-dev__5825600d/`
- No held-out items or results were inspected.

## Preregistered criteria

The thresholds remain proposed and pending team lead approval, as stated in
[`04_evaluation_method.md`](./04_evaluation_method.md). Twelve of 13 criteria
pass; evidence grounding is 0.4 percentage points below its threshold.

| Criterion | Observed | Threshold | Result |
|---|---:|---:|---|
| Strict schema-valid rate | 100.0% | at least 95.0% | Pass |
| Schema-valid or recovered rate | 100.0% | at least 99.0% | Pass |
| Quiz target non-null rate | 97.3% | at least 90.0% | Pass |
| Quiz exact-band accuracy | 67.1% | at least 60.0% | Pass |
| Quiz within-one-band rate | 100.0% | at least 90.0% | Pass |
| Quiz MAE | 0.073 | at most 0.15 | Pass |
| Quiz direction accuracy | 100.0% | at least 90.0% | Pass |
| Quiz Spearman rho | 0.918 | at least 0.80 | Pass |
| Quiz polarity-inversion rate | 0.0% | at most 2.0% | Pass |
| Evidence grounding | 97.6% | at least 98.0% | **Fail** |
| T06 violations | 0 | equal 0 | Pass |
| Edge-case pass rate | 83.0% | at least 80.0% | Pass |
| Organic situational-factor recall | 100.0% | at least 80.0% | Pass |

Other notable results: all 100 responses strictly parsed and passed schema and
semantic validation; organic situational-factor precision was 60.0%, and
category agreement was 0.0%. Organic score MAE was 0.105 and exact-band
accuracy was 46.7%. These organic estimates are based on a small sample.

Quiz target-trait exact-band accuracy was 50.0% for T01 and T04, versus 66.7%
for T02, 86.7% for T03, and 80.0% for T05. All quiz predictions were within one
band of gold and none were polarity inversions.

## Error log by taxonomy, source, and trait

The log contains 72 rows: 62 evaluator error rows and 10 deterministic
`needs_manual_review` flags. Review flags are not automatic findings. One item
can contribute multiple rows.

| Taxonomy | Total rows | Quiz | Organic | Edge |
|---|---:|---:|---:|---:|
| `score_deviation` | 32 | 24 | 8 | 0 |
| `needs_manual_review` | 10 | 9 | 1 | 0 |
| `edge_case_failure` | 8 | 0 | 0 | 8 |
| `unsupported_inference` | 6 | 0 | 6 | 0 |
| `context_confusion` | 5 | 0 | 5 | 0 |
| `missed_signal` | 4 | 2 | 2 | 0 |
| `evidence_not_grounded` | 4 | 0 | 4 | 0 |
| `status_error` | 1 | 1 | 0 | 0 |
| `polarity_inversion` | 1 | 0 | 1 | 0 |
| `confidence_miscalibration` | 1 | 0 | 1 | 0 |
| `malformed_output` | 0 | 0 | 0 | 0 |
| `t06_violation` | 0 | 0 | 0 | 0 |
| **Total** | **72** | **36** | **28** | **8** |

`score_deviation` counts by source and trait:

| Source | T01 | T02 | T03 | T04 | T05 | Total |
|---|---:|---:|---:|---:|---:|---:|
| Quiz | 7 | 5 | 2 | 7 | 3 | 24 |
| Organic | 0 | 2 | 3 | 2 | 1 | 8 |

Other trait-specific errors:

| Error type | Source | Trait | Count | Items |
|---|---|---|---:|---|
| `missed_signal` | Quiz | T01 | 1 | Q04_C |
| `missed_signal` | Quiz | T04 | 1 | Q19_C |
| `missed_signal` | Organic | T01 | 1 | ORG20 |
| `missed_signal` | Organic | T05 | 1 | ORG20 |
| `unsupported_inference` | Organic | T01 | 1 | ORG14 |
| `unsupported_inference` | Organic | T02 | 1 | ORG14 |
| `unsupported_inference` | Organic | T03 | 1 | ORG17 |
| `unsupported_inference` | Organic | T05 | 3 | ORG09, ORG11, ORG14 |
| `evidence_not_grounded` | Organic | T01, T02, T03, T05 | 1 each | ORG14 |
| `polarity_inversion` | Organic | T02 | 1 | ORG11 |
| `confidence_miscalibration` | Organic | T02 | 1 | ORG11 |

The five `context_confusion` rows are one each for ORG02, ORG09, ORG11, ORG12,
and ORG20; none is assigned to one particular trait. The eight
`edge_case_failure` rows come from four edge items: EDGE03, EDGE04, EDGE06, and
EDGE09. The 10 manual-review flags cover nine quiz items and ORG11. No
malformed-output or T06-violation row was recorded.

## Representative failures

The raw outputs below are the saved `response_text` values, not the separately
stored reasoning text.

### ORG11 — situational context treated as pressure and trait evidence

**Input (`decision_text`):** `I turned down a higher-paying job in another city
to stay near my aging parents.`

**Gold:** T02 = 0.6, T03 = 0.15; other traits null. Gold situational factor:
`other`, described as caregiving framed as a value rather than a constraint.

**Raw output:**

```json
{
  "decision_id": "ORG11",
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
      "score": 0.15,
      "confidence": 0.85,
      "evidence": ["I turned down a higher-paying job in another city to stay near my aging parents."],
      "situational_factor": {
        "category": "family_pressure",
        "description": "caring for aging parents"
      },
      "context_notes": "Explicit trade-off between higher future pay and staying near aging parents indicates a strongly present-focused orientation."
    },
    {
      "trait_id": "T03",
      "trait_name": "Locus of Priority",
      "score": 0.15,
      "confidence": 0.85,
      "evidence": ["I turned down a higher-paying job in another city to stay near my aging parents."],
      "situational_factor": {
        "category": "family_pressure",
        "description": "caring for aging parents"
      },
      "context_notes": "Decision prioritizes parents' needs over personal financial gain, showing a strongly other-centered stance."
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
      "score": 0.15,
      "confidence": 0.6,
      "evidence": ["I turned down a higher-paying job in another city to stay near my aging parents."],
      "situational_factor": {
        "category": "family_pressure",
        "description": "caring for aging parents"
      },
      "context_notes": "Choice driven by desire to be near parents reflects emotional weighting over analytical financial considerations."
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

**Diagnosis:** The text states a preference to stay near parents but does not
state that the parents applied pressure. The output labels caregiving as
`family_pressure`, infers an emotional-versus-analytical weighting from the
same preference, and treats pay/location as an explicit time trade-off. The
T02 gold assignment itself is questionable because the narrative does not
clearly express a near-term versus long-term preference; see gold/ontology
notes below.

### EDGE03 — hard constraint mistaken for analytical weighting

**Input (`decision_text`):** `I accepted the only apartment I could afford
because the other available places were outside my budget; I had no realistic
alternative.`

**Gold edge expectation:** all traits null, situational factor present,
maximum confidence 0.2. The output scored T05 = 0.7 and returned success.

**Raw output:**

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

**Diagnosis:** The output recognizes the constraint but then treats the
constraint itself as evidence of analytical reasoning. No comparison,
analysis process, or emotional-versus-analytical weighting is stated. This is
the clearest example of a situational factor being mistaken for a trait signal.

### ORG14 — unsupported trait scores and non-grounded evidence strings

**Input (`decision_text`):** `I've turned down three promotions in a row
because each one would have meant more travel and less time with my kids.`

**Gold:** T03 = 0.15; T01, T02, T04, and T05 null; T06 = 0.85 in the supplied
gold.

**Raw output:**

```json
{"decision_id":"ORG14","extraction_status":"success","traits":[{"trait_id":"T01","trait_name":"Risk Tolerance","score":0.3,"confidence":0.6,"evidence":["\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""],"situational_factor":null,"context_notes":"The decision reflects a trade‑off between career advancement (potential reward) and increased travel (potential negative outcome). The person chooses to avoid the negative outcome, indicating a risk‑averse stance (moderate evidence)."},{"trait_id":"T02","trait_name":"Time Horizon","score":0.15,"confidence":0.6,"evidence":["\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""],"situational_factor":null,"context_notes":"The reasoning explicitly favors present family time over future career benefits, showing a strongly present‑focused orientation (moderate evidence)."},{"trait_id":"T03","trait_name":"Locus of Priority","score":0.1,"confidence":0.6,"evidence":["\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""],"situational_factor":null,"context_notes":"The person prioritizes the interests of their children over their own career advancement, indicating a strongly other‑centered priority (moderate evidence)."},{"trait_id":"T04","trait_name":"Decisiveness Speed","score":null,"confidence":0.0,"evidence":[],"situational_factor":null,"context_notes":"No information about the speed or deliberation process of the decision is provided."},{"trait_id":"T05","trait_name":"Emotional vs. Analytical Weighting","score":0.25,"confidence":0.6,"evidence":["\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""],"situational_factor":null,"context_notes":"The justification is based on personal values (time with kids) rather than analytical data, indicating an emotion‑leaning weighting (moderate evidence)."},{"trait_id":"T06","trait_name":"Self-Consistency","score":null,"confidence":0.0,"evidence":[],"situational_factor":null,"context_notes":"History is unavailable in this task."}]}
```

**Diagnosis:** The evidence strings add literal quotation-mark characters that
are absent from the narrative, causing four grounding errors. The model also
scores T01, T02, and T05 where gold is null. T06 = null follows the prompt's
Task 4 rule, even though gold contains a numeric T06 value; that disagreement
is a gold/contract issue, not a prompt failure to fix by copying gold.

## Situational-factor confusion

- ORG02 receives `family_pressure` even though the text says the person chose
  the career assignment despite the partner's preference; no pressure or
  override is stated.
- ORG11 is labeled `family_pressure` in the model output although the gold
  describes caregiving as a value.
- ORG20 receives `financial_dependency` from a plan to live with parents and
  save for a home, although the narrative does not state financial
  dependence or a hard limitation.
- EDGE03 converts a budget constraint into T05 analytical weighting.
- ORG09 and ORG12 have explicit interpersonal influence, but the gold
  situational-factor category is `low_stakes` while the model chooses
  `social_influence`; these cases also expose overlapping category semantics.

## Gold and ontology issues — listed separately; gold was not changed

1. **Overlapping factor categories (ORG09, ORG12):** `low_stakes` describes
   decision significance, while `social_influence` describes a causal
   mechanism. The input narratives can satisfy both, but the output supports
   only one category. The zero category-agreement result may therefore reflect
   a gold/ontology category-selection ambiguity as well as model behavior.
2. **ORG11 T02:** the gold score is 0.6, but the narrative does not clearly
   describe a present-versus-future trade-off as required by the T02
   definition. The model's 0.15 is not supported either; do not tune to either
   numeric label without annotation review.
3. **ORG11 factor semantics:** the gold maps caregiving framed as a personal
   value to a situational factor of `other`, although the ontology distinguishes
   stable preferences from temporary circumstances. This boundary needs
   annotation guidance, not silent prompt-specific label matching.
4. **ORG14 T06:** gold is 0.85 based on repeated decisions, while the Task 4
   prompt and contract require T06 to remain null because history is unavailable
   to this extraction task. The model's null is contract-compliant. Gold was
   left unchanged.
5. **ORG14 evidence annotation:** the gold evidence is annotation rationale,
   not a literal quote, as documented in the evaluation method. Grounding must
   be checked against the input text, not this rationale.

## Error pattern assessment

The failures are **partly systematic, not purely random**. Twenty-four quiz
score deviations cluster around the inner bands for extreme gold answers:
low anchors are often predicted one band higher and high anchors one band
lower. This is consistent with conservative band compression, although all
predictions remain within one band and the 15-item-per-trait samples are small.
Situational-factor confusion recurs on five distinct organic items, and EDGE03
shows the related tendency to convert a constraint into trait evidence.

Other issues are localized: all four evidence-grounding rows come from one
organic item (ORG14), and the single polarity inversion/manual-review concern
is ORG11. These do not justify broad changes to evidence quoting or score
calibration without additional evidence. The organic and edge datasets are
small and their annotations have the limitations above.

## v2.1 draft and required validation

The five distinct `context_confusion` items meet the preregistered
systematic-category threshold (at least five dev items; also 5/14 organic dev
items). A general clarification was added in v2.1: factor categories must be
supported by their causal role, and a circumstance or constraint alone is not
trait evidence. It contains no item-specific language, gold text, or copied
edge/gold example.

`v2.1` is registered as **draft**, not frozen or accepted. Its separate dev
run and comparison have not been performed because this session cannot call
the model API. It can be kept only if the dev run improves contextual-factor
errors without a regression greater than two percentage points on any other
headline metric. The paired numeric comparison does not itself compare factor
category agreement or edge checks; inspect both run reports for those
measures. Do not change any gold annotation.
