# Dev-split error analysis and prompt comparison

## Scope and run

- Baseline run: `v2.0__openai-gpt-oss-120b__all-dev__5825600d`
- Candidate run: `v2.1__openai-gpt-oss-120b__all-dev__5825600d`
- Prompts: `v2.0` (`6f93b33d…`) and `v2.1` (`7c66c1eb…`)
- Model: `openai/gpt-oss-120b`; 100 responses; dev split only (75 quiz, 14
  organic, 11 edge cases)
- Evaluations: `evaluation/results/` for both runs; paired comparison in
  `evaluation/comparisons/`
- No held-out items or results were inspected.

## Preregistered criteria

The thresholds remain proposed and pending team lead approval, as stated in
[`04_evaluation_method.md`](./04_evaluation_method.md). The evaluator's quote
normalization was corrected to ignore balanced surrounding quote delimiters.
The results below are from both runs re-evaluated with that correction; prompt,
gold, eval-set, and raw-response files were unchanged. v2.0 passes all 13
criteria; v2.1 passes 12 and fails organic situational-factor recall.

| Criterion | Threshold | v2.0 | v2.1 |
|---|---:|---:|---:|
| Strict schema-valid rate | at least 95.0% | 100.0% Pass | 100.0% Pass |
| Schema-valid or recovered rate | at least 99.0% | 100.0% Pass | 100.0% Pass |
| Quiz target non-null rate | at least 90.0% | 97.3% Pass | 94.7% Pass |
| Quiz exact-band accuracy | at least 60.0% | 67.1% Pass | 73.2% Pass |
| Quiz within-one-band rate | at least 90.0% | 100.0% Pass | 98.6% Pass |
| Quiz MAE | at most 0.15 | 0.073 Pass | 0.064 Pass |
| Quiz direction accuracy | at least 90.0% | 100.0% Pass | 100.0% Pass |
| Quiz Spearman rho | at least 0.80 | 0.918 Pass | 0.916 Pass |
| Quiz polarity-inversion rate | at most 2.0% | 0.0% Pass | 0.0% Pass |
| Evidence grounding | at least 98.0% | 100.0% Pass | 100.0% Pass |
| T06 violations | equal 0 | 0 Pass | 0 Pass |
| Edge-case pass rate | at least 80.0% | 83.0% Pass | 85.1% Pass |
| Organic situational-factor recall | at least 80.0% | 100.0% Pass | 66.7% **Fail** |

Both runs strictly parsed and passed schema and semantic validation on all 100
items. Organic situational-factor precision/category agreement were 60.0%/0.0%
for v2.0 and 50.0%/0.0% for v2.1. Organic score MAE/exact-band accuracy were
0.105/46.7% and 0.104/46.2%, respectively. Organic estimates are based on a
small sample. v2.1 has better quiz score metrics and edge-case pass rate, but
its factor recall regression fails a readiness criterion; v2.0 is therefore
the preferred version under the preregistered criteria.

## Error log by taxonomy, source, and trait

The regenerated v2.0 log contains 68 rows: 58 evaluator error rows and 10
deterministic `needs_manual_review` flags. Review flags are not automatic
findings. One item can contribute multiple rows.

| Taxonomy | Total rows | Quiz | Organic | Edge |
|---|---:|---:|---:|---:|
| `score_deviation` | 32 | 24 | 8 | 0 |
| `needs_manual_review` | 10 | 9 | 1 | 0 |
| `edge_case_failure` | 8 | 0 | 0 | 8 |
| `unsupported_inference` | 6 | 0 | 6 | 0 |
| `context_confusion` | 5 | 0 | 5 | 0 |
| `missed_signal` | 4 | 2 | 2 | 0 |
| `status_error` | 1 | 1 | 0 | 0 |
| `polarity_inversion` | 1 | 0 | 1 | 0 |
| `confidence_miscalibration` | 1 | 0 | 1 | 0 |
| `malformed_output` | 0 | 0 | 0 | 0 |
| `t06_violation` | 0 | 0 | 0 | 0 |
| **Total** | **68** | **36** | **24** | **8** |

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
| `polarity_inversion` | Organic | T02 | 1 | ORG11 |
| `confidence_miscalibration` | Organic | T02 | 1 | ORG11 |

The five `context_confusion` rows are one each for ORG02, ORG09, ORG11, ORG12,
and ORG20; none is assigned to one particular trait. Quote normalization
removed the four former ORG14 `evidence_not_grounded` rows. The eight
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

**Diagnosis:** Each of the four evidence strings is the exact narrative
excerpt, wrapped in balanced quotation marks. The original matcher treated
those delimiters as quote content and falsely marked the evidence ungrounded.
After evaluator normalization was corrected, all four quotes pass grounding;
this is an evaluator artifact, not fabricated evidence. The model also scores
T01, T02, and T05 where gold is null. T06 = null follows the prompt's Task 4
rule, even though gold contains a numeric T06 value; that disagreement is a
gold/contract issue, not a prompt failure to fix by copying gold.

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

Other issues are localized: the only apparent evidence-grounding issue was
the ORG14 matcher artifact described above, and the single polarity
inversion/manual-review concern is ORG11. These do not justify broad changes to
evidence quoting or score calibration without additional evidence. The organic
and edge datasets are small and their annotations have the limitations above.

## v2.1 dev comparison and decision

The five distinct `context_confusion` items meet the preregistered
systematic-category threshold (at least five dev items; also 5/14 organic dev
items). A general clarification was added in v2.1: factor categories must be
supported by their causal role, and a circumstance or constraint alone is not
trait evidence. It contains no item-specific language, gold text, or copied
edge/gold example.

The separate v2.1 dev run and paired comparison are complete. v2.1 improved
quiz exact-band accuracy (67.1% to 73.2%), quiz MAE (0.073 to 0.064), and edge
checks (83.0% to 85.1%). However, organic situational-factor recall fell from
100.0% to 66.7%, below the proposed 80.0% readiness threshold; precision also
fell from 60.0% to 50.0%. Both versions had 0.0% category agreement. That
metric excludes ambiguous-gold records, so v2.0's category matches on
ambiguous ORG05/ORG18 do not count; its eligible true-positive categories
(ORG09, ORG11, ORG12) all differ from gold. v2.1's eligible true positives
(ORG09, ORG12) also both differ.

The evaluator records a factor detection when at least one factor category is
predicted, and separately compares its category with gold; the 0.0% agreement
is not a mapping bug. The regression is a model miss on an eligible gold factor
(ORG05 in v2.1), not a category-name normalization issue.

**Decision:** retain v2.0 as the preferred baseline under the preregistered
criteria. Keep v2.1 as a draft, not the selected version: its additional edge
check and quiz-score gains do not compensate for failing the factor-recall
criterion. Its missed eligible gold factor is ORG11. Reconsider v2.1 only
after addressing factor recall and evaluating on a separately run dev set; do
not alter gold annotations to improve either score.
