# WP2 Storage Layer Design

Authored by: coding agent (lead run)
Date: 2026-11-27

## 1. Scope

WP2 owns the SQLite storage layer for the Decision Mirror profile engine. It is a Wave 1 design deliverable; no storage implementation is included in this document's change set.

The design follows Chapter 3, section 3.3. It supports append-only decision history, user isolation, session lifecycle rules, extraction provenance, and complete account deletion.

## 2. Tables

All date/time columns use ISO-8601 UTC strings. SQLite stores these as `TEXT`.

### 2.1 `users`

| Column | Type | Constraints |
|---|---|---|
| `user_id` | TEXT | PRIMARY KEY |
| `created_at` | TEXT | NOT NULL |

### 2.2 `sessions`

| Column | Type | Constraints |
|---|---|---|
| `decision_id` | TEXT | PRIMARY KEY |
| `session_id` | TEXT | NOT NULL, UNIQUE |
| `user_id` | TEXT | NOT NULL, FOREIGN KEY -> `users.user_id` |
| `decision_text` | TEXT | NOT NULL |
| `decision_date` | TEXT | NOT NULL |
| `approval_date` | TEXT | NULL |
| `status` | TEXT | NOT NULL; `pending`, `approved`, or `rejected` |
| `prompt_version` | TEXT | NOT NULL |
| `prompt_sha256` | TEXT | NOT NULL |
| `model_version` | TEXT | NOT NULL |
| `advisor_top_choice_approved` | INTEGER | NULL or 0/1 |
| `synthetic` | INTEGER | NOT NULL, default 0 |

`decision_id` is the primary key and matches `DecisionRecord.decision_id`.
`decision_date` is when the decision occurred.
`approval_date` is when the session was approved.
They are separate columns and a late approval must not rewrite `decision_date`.

### 2.3 `chat_messages`

| Column | Type | Constraints |
|---|---|---|
| `message_id` | TEXT | PRIMARY KEY |
| `session_id` | TEXT | NOT NULL, FOREIGN KEY -> `sessions.session_id` |
| `user_id` | TEXT | NOT NULL, FOREIGN KEY -> `users.user_id` |
| `role` | TEXT | NOT NULL; `user` or `system` |
| `text` | TEXT | NOT NULL |
| `created_at` | TEXT | NOT NULL |

Storing `user_id` directly provides explicit user isolation at the repository boundary.

### 2.4 `extraction_results`

| Column | Type | Constraints |
|---|---|---|
| `decision_id` | TEXT | PRIMARY KEY, FOREIGN KEY -> `sessions.decision_id` |
| `session_id` | TEXT | NOT NULL, UNIQUE, FOREIGN KEY -> `sessions.session_id` |
| `user_id` | TEXT | NOT NULL, FOREIGN KEY -> `users.user_id` |
| `extraction_status` | TEXT | NOT NULL; `success`, `insufficient_evidence`, or `error` |
| `prompt_version` | TEXT | NOT NULL |
| `prompt_sha256` | TEXT | NOT NULL |
| `model_version` | TEXT | NOT NULL |
| `error_type` | TEXT | NULL |
| `error_message` | TEXT | NULL |
| `schema_valid` | INTEGER | NULL or 0/1 |
| `semantic_valid` | INTEGER | NULL or 0/1 |
| `warnings_json` | TEXT | NULL |
| `created_at` | TEXT | NOT NULL |

The error fields and validation fields preserve the `ExtractionResult` pipeline envelope.
`traits` is represented by the `observations` table for successful extraction outputs.

### 2.5 `observations`

| Column | Type | Constraints |
|---|---|---|
| `observation_id` | TEXT | PRIMARY KEY |
| `decision_id` | TEXT | NOT NULL, FOREIGN KEY -> `sessions.decision_id` |
| `session_id` | TEXT | NOT NULL, FOREIGN KEY -> `sessions.session_id` |
| `user_id` | TEXT | NOT NULL, FOREIGN KEY -> `users.user_id` |
| `trait_id` | TEXT | NOT NULL; `T01` through `T06` |
| `score` | REAL | NULL or 0.0 through 1.0 |
| `confidence` | REAL | NOT NULL, 0.0 through 1.0 |
| `evidence_json` | TEXT | NOT NULL |
| `situational_factor_json` | TEXT | NULL |
| `context_notes` | TEXT | NOT NULL |
| `source` | TEXT | NOT NULL; `quiz` or `decision` |
| `created_at` | TEXT | NOT NULL |

A null score requires confidence `0.0` and an empty evidence list.
A quiz observation is stored with `source = 'quiz'`; a decision observation uses `source = 'decision'`.

## 3. Model-to-column reconciliation

| Model or field | Database representation | Mismatch status |
|---|---|---|
| `TraitObservation.trait_id` | `observations.trait_id` | Match |
| `TraitObservation.score` | `observations.score` nullable REAL | Match |
| `TraitObservation.confidence` | `observations.confidence` | Match |
| `TraitObservation.evidence` | `observations.evidence_json` | Name is adapted to JSON storage; value matches the model |
| `TraitObservation.situational_factor` | `observations.situational_factor_json` | Name is adapted to JSON storage; value matches the model |
| `TraitObservation.context_notes` | `observations.context_notes` | Match |
| `TraitObservation.source` | `observations.source` | Match |
| `DecisionRecord.decision_id` | `sessions.decision_id` | Match |
| `DecisionRecord.user_id` | `sessions.user_id` | Match |
| `DecisionRecord.session_id` | `sessions.session_id` | Match |
| `DecisionRecord.decision_text` | `sessions.decision_text` | Match |
| `DecisionRecord.decision_date` | `sessions.decision_date` | Match |
| `DecisionRecord.approval_date` | `sessions.approval_date` | Match |
| `DecisionRecord.status` | `sessions.status` | Match |
| `DecisionRecord.prompt_version` | `sessions.prompt_version` | Match |
| `DecisionRecord.prompt_sha256` | `sessions.prompt_sha256` | Match |
| `DecisionRecord.model_version` | `sessions.model_version` | Match |
| `DecisionRecord.advisor_top_choice_approved` | `sessions.advisor_top_choice_approved` | Match |
| `DecisionRecord.synthetic` | `sessions.synthetic` | Match |
| `ExtractionResult.model_version`, `prompt_version`, `prompt_sha256` | `extraction_results` matching columns | Match |

No unresolved model-name mismatch remains. JSON columns are used only where the Pydantic model contains a list or nested object.

## 4. Relationships

```text
users 1 ---> N sessions
users 1 ---> N chat_messages
sessions 1 ---> N chat_messages
sessions 1 ---> 0..1 extraction_results
extraction_results 1 ---> N observations
```

All tables use foreign keys and direct `user_id` ownership columns where user-scoped queries must remain explicit.

## 5. Session lifecycle invariants

### Pending

- A pending session has chat messages.
- It has no extraction result and no observations.
- It must not accept extraction or observation writes.

### Rejected

- A rejected session keeps its chat messages.
- It has no extraction result and no observations.

### Approved

- An approved session may have one extraction result.
- It may have observations produced from that extraction result.
- Only approved sessions have extraction results and observations.

## 6. Append-only observations

Observations are append-only in two independent layers:

1. SQLite triggers reject `UPDATE` and `DELETE` statements on `observations`, with one carefully defined exception: deleting a user activates a temporary or transaction-scoped account-deletion context that permits cascade deletion of that user's observations.
2. Python repositories expose only append and read methods for observations. There are no update or delete methods.

The exception must permit only an account deletion transaction. Direct SQL updates/deletes and any observation deletion not initiated by `delete_user(user_id)` must abort.
For table identity, the trigger checks the observation's `user_id` against a temporary deletion marker set by `delete_user`.

## 7. Account deletion

`delete_user(user_id)` removes every row owned by that user from `observations`, `extraction_results`, `chat_messages`, `sessions`, and `users`.
It changes no row owned by another user.
The implementation uses a single transaction, foreign keys, parameterized SQL, and the whole-user deletion exception for observation triggers.
`extraction_results` and `observations` are removed before `sessions`; chat messages are removed before sessions.

## 8. Repository interfaces

Every method takes `user_id` as the first argument.

### `UserRepository`

```text
create_user(user_id: str, created_at: str) -> None
user_exists(user_id: str) -> bool
delete_user(user_id: str) -> None
```

### `SessionRepository`

```text
create_session(user_id: str, decision_id: str, session_id: str, decision_text: str,
               decision_date: str, approval_date: str | None, status: str,
               prompt_version: str, prompt_sha256: str, model_version: str,
               advisor_top_choice_approved: bool | None, synthetic: bool) -> None
get_session(user_id: str, decision_id: str) -> DecisionRecord | None
list_sessions(user_id: str) -> list[DecisionRecord]
update_session_status(user_id: str, decision_id: str, status: str,
                      approval_date: str | None) -> None
```

Session status may be updated, but observations remain append-only.
The repository deliberately has no session deletion method in this design.

### `ChatMessageRepository`

```text
append_chat_message(user_id: str, session_id: str, message_id: str,
                    role: str, text: str, created_at: str) -> None
list_chat_messages(user_id: str, session_id: str) -> list[dict]
```

### `ObservationRepository`

```text
append_observation(user_id: str, decision_id: str, observation: TraitObservation,
                   created_at: str) -> None
list_observations(user_id: str, decision_id: str) -> list[TraitObservation]
list_user_observations(user_id: str) -> list[TraitObservation]
```

This repository has append and read methods only.
It has no update and no delete method.

### `ExtractionResultRepository`

```text
save_extraction_result(user_id: str, decision_id: str,
                       result: ExtractionResult) -> None
get_extraction_result(user_id: str, decision_id: str) -> ExtractionResult | None
```

## 9. Extraction result contents

An extraction result stores:

- `prompt_version`;
- `prompt_sha256`;
- `model_version`;
- `decision_id`;
- `session_id`;
- `extraction_status`;
- pipeline `error`, if present;
- pipeline `validation`, if present;
- output traits are stored as append-only observation rows.

## 10. SQLite implementation rules

- Use the standard library `sqlite3` package only.
- Enable foreign keys with `PRAGMA foreign_keys = ON`.
- Use parameterized queries only; never format SQL from caller values.
- Support `:memory:` and file database paths with the same class.
- Enforce lifecycle and ownership checks in repositories.
- Use explicit transactions for account deletion and multi-row writes.

## 11. Open questions

- The session identifier and decision identifier need a final uniqueness convention; the design currently uses `decision_id` as the record primary key and requires `session_id` to be unique.
- The retention format for rejected-session chat messages is not finalized beyond retaining them.
- Trigger syntax for the whole-user deletion exception should be reviewed against the final SQLite implementation and test suite.
