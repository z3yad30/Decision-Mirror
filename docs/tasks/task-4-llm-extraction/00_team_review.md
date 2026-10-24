# Summary

The Task 4 materials are not ready for reproducible evaluation. The prompts, schema, runner, and gold data are internally inconsistent; key evaluation deliverables are missing. The decisions below define a safer, measurable baseline for subsequent prompts.

# Findings by artifact

## Shams — prompts v1.0–v1.3

1. **Gold leakage.** v1.2/v1.3 contain a "Special Calibration Rule for D001" that hard-codes the gold answer (T01=0.30/0.72, T02=0.40/0.45) for the exact D001 sentence. Any evaluation including that sentence is invalid. It is removed from the plan: no prompt may contain gold values.
2. **Version record is not reproducible.** Only v1.3 is complete. v1.1 is a summary, and v1.2 is stored in reverse block order. No prompt exists as a file, hash, or registry.
3. **Prompt contradicts the team's own ontology gold.** v1.3 says a spreadsheet alone is insufficient for T05 and requires an explicit near-term vs. long-term trade-off for T02. Ontology §9 Decision 3 scores T05=0.90 from "three weeks… with a spreadsheet", and Decision 2 scores T02=0.70 from "the right step for my career". The gates are stricter than the gold they will be graded on.
4. **No onboarding-quiz handling.** v1.0 mentioned it. v1.3 dropped it. Quiz answers are single short choices; the evidence gates would null nearly all of them, but the quiz gold has a numeric value for every record.
5. **Output fields drift from the ontology.** The ontology §4 specifies evidence as a list and a situational_factor field, and §3.1 defines a four-way split (trait / explicit preference / situational factor / external constraint). Prompts use evidence as a string, no situational_factor, and fold everything into free-text context_notes.
6. **model_version is LLM-generated ("GPT-6" in the outputs).** A model cannot reliably know its own identifier. The pipeline must inject it.
7. **Status semantics contradict.** v1.2: success means ≥1 numeric score. v1.3: success even if all scores are null. Habiba's spec doesn't say.
8. **Overlapping score bands (0.2 belongs to two bands).** Needs half-open intervals.
9. **Testing basis is too thin.** 3 ad-hoc inputs run by hand in a chat UI (D002 and D003 have no gold) and a different model from the one in Ahmed's runner (Groq openai/gpt-oss-20b). Calibration to one model does not transfer.

## Habiba — schemas

10. The JSON Schema in the PDF is not valid JSON: curly quotes and an unquoted $schema URL. It is not machine-usable.
11. score is typed number and non-nullable, but T06 must be null and the prompts use null for insufficient evidence. The schema rejects its own required behavior.
12. No additionalProperties:false; trait_id and trait_name are free strings instead of enums; the traits array has no min/max (should be exactly 6, T01–T06, unique).
13. No situational_factor; evidence is a string; no rule tying confidence to null scores; no rule tying extraction_status to the trait contents.
14. There is no input JSON Schema, no quiz-input mapping, and no length limits. Input spec says "Unsupported fields must be ignored", which would silently pass gold fields into a request.
15. model_version and prompt_version are required in the LLM output, but they should be pipeline-injected metadata.
16. The brief required valid and invalid output examples, schema test cases, and malformed-output handling. None were delivered, and the malformed-output policy is one line.

## Ahmed Osama — main.py

17. Not resumable and not batchable. Re-running appends every record again (duplicates). There is no way to run 10 at a time.
18. 429 detection is a substring match on the error text. After 3 failures it writes a final error row, so a rate-limited item looks like a model failure.
19. No schema validation, no JSON parsing, no recorded model/prompt version, temperature, token usage, latency, or timestamps.
20. Reads prompt.txt from the working directory: the prompt is unversioned, and a run can't be tied to a prompt version.
21. Uses record_id as both decision_id and user_id; puts scenario and answer into one string with no documented format; hard-codes ontology_version: "v1.0".
22. Does not set temperature (non-deterministic runs), and does not guard against reasoning text vs. final content for a reasoning model.

## Gold dataset

23. 125 quiz records only (25 questions × 5 options). The ontology's 20 annotated organic narratives (§9), which the brief says are also gold, are not in the dataset, so there is no gold for free-text decision logs, situational factors, multi-trait cases, or null cases.
24. Every record has confidence: 0.70, situational_factor: null, and a template evidence string. The dataset itself flags the 0.70 vs. 0.90 inconsistency with Task 3. Consequences: confidence agreement and evidence agreement cannot be measured on the quiz set the way the brief asks. Evidence must be judged by grounding, not text match.
25. Gold has one target trait per record; an LLM that also scores other traits is not necessarily wrong. This must be measured separately.
26. Ontology §9 Decisions 4 and 5 have value "—" but non-zero confidence (0.35, 0.20), and §10 Case 1 says to score the stated preference at reduced confidence. The gold is internally ambiguous: these items are flagged ambiguous_gold and reported separately.

# Missing deliverables

27. Mohamed Abdelhakam's: metric definitions, evaluation script, analysis tables, error taxonomy, quantitative results (only the raw dataset exists).
28. Mohamed Ali's: edge-case test set, prompt review checklist, cross-review findings.
29. Ahmed Osama's: schema-compliance report, structured error log (decision ID, expected, actual, error type, severity, notes), difficult-case examples.
30. Task 4.5: the evaluation report and readiness decision. The brief's evaluation-by-prompt-version separation is impossible without a prompt registry.
31. No dev vs. held-out separation, so iterating on the prompt against the same items that will be reported would overfit.

# Decisions taken in this plan

The team lead may veto these decisions.

- The LLM output contains only decision_id, extraction_status, traits. model_version and prompt_version are added by the pipeline in a result envelope.
- Exactly six traits, T01–T06, always present. Unsupported → score: null, confidence: 0.0, evidence: []. T06 is always null in Task 4.
- extraction_status: success iff at least one non-null score; insufficient_evidence iff all six are null; error is pipeline-only (never emitted by the model).
- evidence is a list of exact quotes from decision_text. situational_factor is null or {category, description}.
- Quiz extraction is blind: the model is not told which trait the question targets. Off-target scoring is measured, not penalized in headline error.
- Two gold sets (quiz: 125; organic: 20 transcribed from the ontology) plus a small self-authored edge-case set with expected behaviors, not numeric gold.
- Quiz hold-out: 2 of the 5 questions per trait are held out; no prompt edits are made from hold-out results.
- The legacy v1.x prompts are archived, not evaluated.

# Open questions for the team lead

- Resolve the quiz gold confidence 0.70 vs. 0.90 inconsistency.
- Resolve ontology §9 Decision 4 (score "—" vs. "record the stated preference").
- Approve the readiness thresholds in Prompt 6.
