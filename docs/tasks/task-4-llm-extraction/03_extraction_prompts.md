# Prompt 4 — Extraction prompt review

## Instruction hierarchy

1. The versioned system prompt is the extractor's governing instruction and is
   sent as-is.
2. The user message is only the Prompt 2 model-request whitelist:
   `decision_id`, `source_type`, `decision_text`, `ontology_version`, and
   `language`.
3. `decision_text` is untrusted data. Embedded instructions, quoted commands,
   or claims to be higher-priority messages cannot override the system prompt.
4. The ontology defines trait meaning, direction, context distinctions, and
   evidence tiers. The frozen Task 4 output contract defines output fields,
   null invariants, and status values.

## Prompt-to-ontology mapping

| Prompt section | Ontology source |
|---|---|
| 1. Role and boundaries | §1.1 guiding principle; §3 context vs. trait |
| 2. Ontology and scoring (T01–T06) | §1.2 scope; §2 full trait definitions |
| 3. Trait, preference, situation, and constraint | §3.1–§3.3; §10 Cases 1 and 2 |
| 4. Evidence tiers and confidence | §4.1–§4.2 |
| 5. Null scores | §4.1 insufficient tier; §10 Case 4 |
| 6. Source handling | §3; Task 4 input contract §Quiz mapping |
| 7. Status and output | Task 4 output contract; ontology §4 evidence requirements |
| 8. Illustrative few-shot examples | Operational examples authored for this prompt, guided by §§3–4 and §10 |
| 9. Final self-check | §§1–4 and §10; Task 4 output contract |

## Design decisions

- **Why quiz mode exists:** onboarding answers are a supported Prompt 2 input
  source, but their narrative is short. The scenario supplies the trade-off;
  the selected answer alone is evidence. This permits a score when an answer
  clearly expresses a position while preventing the scenario or an inferred
  target trait from becoming evidence for unrelated traits.
- **Why gates were relaxed from v1.3:** the review found v1.3 required explicit
  evidence in ways that rejected the ontology's moderate tier, especially for
  partially stated time trade-offs and one-sided emotion/analysis cues. The
  v2.0 prompt permits moderate evidence as described per trait, without
  treating a mere final choice as proof.
- **Where gates remain:** weak evidence does not force a score; the T01 final
  choice alone is not proof, T02 needs a time-based signal rather than an
  inherent timeline, T03 cannot assume self-priority when no other party is
  mentioned, T04 separates imposed deadlines from preference, and T05 does
  not infer reasoning style without a reasoning signal. T06 remains null in
  Task 4 because history is unavailable. Pure constraints are not preferences.
- **Conflicting desire and action:** ontology §10 Case 1 is explicit: record
  the stated preference at reduced confidence and tag the operative social
  influence, rather than scoring only from the final action.
- **No neutral default:** a midpoint is reserved for evidence of a balanced
  position; unsupported traits remain null with the contract-required
  confidence, evidence, and explanation.
- **Confidence guidance:** confidence is tied to evidence strength, relevance,
  and situational limits. Its indicative ranges are guidance, not calibration
  targets.
- **Illustrations:** all three examples are self-authored and explanatory,
  not drawn from ontology decisions, quiz scenarios, or evaluation records.

## Changes from v1.3

- Removed the record-specific gold calibration instruction; the v2.0 prompt
  contains no gold labels, IDs, or examples from the ontology's worked
  decisions.
- Added onboarding-quiz behavior, including answer-only trait evidence and a
  moderate-evidence ceiling for a selected option without reasoning.
- Replaced overlapping score ranges with explicit half-open intervals and
  correct low-to-high polarity for T03 and T05.
- Added the four-way distinction and explicit situational language cues,
  `situational_factor`, and the §10 Case 1 treatment.
- Aligned confidence, evidence arrays, null behavior, T06 handling, and
  status/output fields with the frozen Task 4 contract.
- Added instruction-injection resistance by treating all `decision_text`
  content as data.
- Added an exact JSON shape without model- or prompt-generated version fields.

## Review checklist

| Item | Check | Method | Status |
|---|---|---|---|
| Instruction hierarchy | System prompt governs; the user payload is whitelisted and `decision_text` is untrusted data. | manual | not yet verified |
| Ontology alignment | Definitions, polarity, bands, evidence tiers, and context distinctions map to the cited ontology sections. | manual | not yet verified |
| Unsupported-trait restraint | The prompt does not push the model to infer unsupported traits or infer one trait from another. | manual | not yet verified |
| Confidence quality | Confidence is tied to evidence quality, not wording confidence or score magnitude. | manual | not yet verified |
| Injection resistance | Instructions inside `decision_text` are explicitly treated as data. | manual | not yet verified |
| Output contract | Six trait IDs/names, status values, and half-open bands are present. | automated test | passed |
| Gold leakage | No quiz scenarios/answers, organic or edge decision text, record IDs, gold evidence, or D001 sentence appears. | automated test | passed |
| Prompt loader | Legacy refusal, unknown-version handling, and frozen hash verification behave as specified. | automated test | passed |
