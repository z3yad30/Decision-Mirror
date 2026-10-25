# Task 4 Output Contract v1.0 — frozen

This contract separates the model response from the pipeline result envelope:

- [`schemas/extraction_output.schema.json`](../../../schemas/extraction_output.schema.json)
  validates the exact JSON returned by the LLM.
- [`schemas/extraction_result.schema.json`](../../../schemas/extraction_result.schema.json)
  validates the envelope assembled by the pipeline; the LLM never emits this
  envelope.

## LLM response fields

| Field | Type | Required | Allowed values / rules |
|---|---|---:|---|
| `decision_id` | string | Yes | Must equal the input ID |
| `extraction_status` | string | Yes | `success` or `insufficient_evidence`; derived from scores |
| `traits` | array | Yes | Exactly six objects in T01, T02, T03, T04, T05, T06 order |

Every trait object has exactly these fields; additional properties are rejected.

| Field | Type | Allowed values / rules |
|---|---|---|
| `trait_id` | string | `T01`–`T06`, in order |
| `trait_name` | string | Must match its ID: Risk Tolerance; Time Horizon; Locus of Priority; Decisiveness Speed; Emotional vs. Analytical Weighting; Self-Consistency |
| `score` | number or null | Number in `[0.0, 1.0]`; null means no supported score |
| `confidence` | number | In `[0.0, 1.0]`; exactly `0.0` when score is null |
| `evidence` | array of strings | Exact quotes from `decision_text`; empty for null scores and non-empty for scored traits |
| `situational_factor` | null or object | Object has exactly `category` and `description`; category is `financial_dependency`, `family_pressure`, `external_deadline`, `external_constraint`, `limited_alternatives`, `social_influence`, `low_stakes`, or `other` |
| `context_notes` | string | May be empty, but must explain null scores for T01–T05 and mention a situational factor when one is assigned |

Ontology §3.1 distinguishes a relatively stable trait, a decision-specific
explicit preference, a temporary situational factor, and an external constraint.
Do not generalize constraints or temporary circumstances into stable traits.
Per §4, insufficient evidence must remain null rather than be guessed or
replaced with a midpoint.

## Semantic validation

Schema validation and semantic validation are separate. The validator returns
`{schema_errors, semantic_errors, warnings}`.

Reject responses when any of these conditions applies:

- Traits are not exactly T01–T06 in order, once each.
- `success` has no non-null score, or `insufficient_evidence` has any non-null score.
- A null score has confidence other than `0.0` or non-empty evidence.
- A non-null score has no evidence.
- T06 is non-null when `context.history` is absent or empty. Task 4 producers
  must omit history, so T06 must be null.
- The response ID differs from the input ID.
- The model emits `error` status. `error` is a pipeline-only status and is not
  allowed by the LLM response schema.
- A null T01–T05 score has empty `context_notes`.

Accept with a warning when evidence is not found after whitespace and quote
normalization (`evidence_not_grounded`), a scored trait has confidence below
`0.2`, or the assigned situational factor is not mentioned in `context_notes`.

## Pipeline result envelope

The pipeline injects `model_version`, `prompt_version`, and `prompt_sha256`.
They are not requested from the LLM because model-generated version metadata
cannot provide reliable provenance. The envelope carries `decision_id`,
`extraction_status` (`success`, `insufficient_evidence`, or pipeline-only
`error`), `traits` (null on error), the injected version metadata, `error`
(null or `{type, message}`), and `validation` (`schema_valid`,
`semantic_valid`, `warnings`).

## Malformed-output policy

Failure types are `empty_response`, `not_json`, `schema_violation`,
`semantic_violation`, and `api_error`. Strict JSON parsing is authoritative.
A separate lenient diagnostic pass may strip Markdown fences or surrounding
prose to set `recovered`; it must never supply data to downstream processing.
Recovered output remains a format failure (`not_json`).

Production callers retry malformed output once automatically. If the retry
also fails, emit an error envelope and log the failure type; never pass partial
trait data downstream. Evaluation callers do not retry and record the first
failure. API errors are classified separately from malformed model text.

## Decision log

- Null plus confidence `0.0` and empty evidence means there is no support for a
  score; a numeric midpoint would falsely imply evidence.
- Status is derived from whether any score is non-null, avoiding conflicting
  model claims about status.
- Model/prompt versions and prompt hash are pipeline-injected for traceable,
  reproducible provenance.
- Unknown fields are rejected rather than ignored so fields such as `gold_value`
  cannot silently cross the input boundary.

**Contract v1.0 is frozen.** Any later contract change requires a version bump
and a changelog entry.
