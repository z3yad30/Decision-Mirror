# Task 4 Input Contract v1.0 — frozen

This contract defines the application-to-extractor request. The machine-readable
schema is [`schemas/extraction_input.schema.json`](../../../schemas/extraction_input.schema.json).

## Fields

| Field | Type | Required | Allowed values / rules | Sent to model |
|---|---|---:|---|---:|
| `decision_id` | string | Yes | 1–64 ASCII letters, digits, `_`, `.`, or `-` | Yes |
| `user_id` | string | Yes | Same identifier pattern as `decision_id` | No |
| `source_type` | string | Yes | `decision_log` or `onboarding_quiz` | Yes |
| `decision_text` | string | Yes | Trimmed length 1–4000; must contain non-whitespace text | Yes |
| `ontology_version` | string | Yes | `v1.0` only | Yes |
| `timestamp` | string | No | ISO-8601 UTC timestamp ending in `Z` | No |
| `language` | string | No | BCP-47 language tag; default is `en` | Yes |
| `context` | object | No | Only `question_id` and reserved `history` are recognized | Only `history`, if present |

All other top-level and context fields are rejected. Silently ignoring unknown
fields is unsafe: a field such as `gold_value` could otherwise pass unnoticed
through application code and contaminate a model request or evaluation.

`context.question_id` is quiz-only and remains in the application. The
`context.history` field is reserved for a future contract version and must be
absent from Task 4 inputs. Accordingly, T06 is always null in Task 4. The
request builder sends only `decision_id`, `source_type`, `decision_text`,
`ontology_version`, and `language`, plus `context.history` only when a future
caller explicitly supplies it; it never sends `user_id`, `timestamp`, or
`question_id`.

## Quiz mapping

Use `build_quiz_payload(scenario, answer_text, question_id, decision_id,
user_id)` in
[`payloads.py`](../../../src/decision_mirror/extraction/payloads.py). It creates
`decision_text` exactly as:

```text
Scenario: <scenario>
Selected answer: <answer_text>
```

Only the scenario and selected answer text enter the model-facing narrative.
The record's `trait_id`, `gold_value`, `evidence`, `confidence`, and other
answer options must never be included.

## Versioning

**Contract v1.0 is frozen.** Any later contract change requires a version bump
and a changelog entry.
