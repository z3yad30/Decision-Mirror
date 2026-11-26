# WP2 Storage Layer Design

## 1. Scope

WP2 owns the deterministic SQLite storage layer for the Decision Mirror profile engine.

The storage layer persists user/session history and extraction provenance. It does not call an LLM and does not perform aggregation itself.

The design supports:

- user-scoped data isolation;
- pending, rejected, and approved session lifecycle rules;
- immutable/append-only trait observations;
- extraction provenance (`prompt_version`, `prompt_sha256`, `model_version`);
- separate decision and approval dates;
- trait scores for decisions ;
- full account deletion for one user;
- SQLite `:memory:` and file-backed databases.

## 2. Tables

### 2.1 `users`

| Column | Type | Constraints |
|---|---|---|
| `user_id` | TEXT | PK |
| `created_at` | TEXT | NOT NULL |

### 2.2 `sessions`

| Column | Type | Constraints |
|---|---|---|
| `session_id` | TEXT | PK |
| `user_id` | TEXT | FK → `users.user_id`, NOT NULL |
| `name` | TEXT | NOT NULL |
| `context_paragraph` | TEXT | NOT NULL |
| `decision_text` | TEXT | NOT NULL |
| `options_json` | TEXT | NOT NULL; JSON array/object representation |
| `status` | TEXT | NOT NULL; `pending`, `rejected`, or `approved` |
| `decision_date` | TEXT | NOT NULL |
| `approval_date` | TEXT | NULL until approved |
| `created_at` | TEXT | NOT NULL |

`decision_date` records when the decision occurred. `approval_date` records when the user approved storage/extraction. A late approval must never rewrite `decision_date`.

### 2.3 `chat_messages`

| Column | Type | Constraints |
|---|---|---|
| `message_id` | TEXT | PK |
| `session_id` | TEXT | FK → `sessions.session_id`, NOT NULL |
| `user_id` | TEXT | FK → `users.user_id`, NOT NULL |
| `role` | TEXT | NOT NULL; `user` or `system` |
| `text` | TEXT | NOT NULL |
| `created_at` | TEXT | NOT NULL |

`user_id` is stored directly as well as being reachable through the session so every repository operation can enforce user ownership cheaply and explicitly.

### 2.4 `extraction_results`

| Column | Type | Constraints |
|---|---|---|
| `result_id` | TEXT | PK |
| `session_id` | TEXT | UNIQUE FK → `sessions.session_id`, NOT NULL |
| `user_id` | TEXT | FK → `users.user_id`, NOT NULL |
| `prompt_version` | TEXT | NOT NULL |
| `prompt_sha256` | TEXT | NOT NULL |
| `model_version` | TEXT | NOT NULL |
| `extraction_status` | TEXT | NOT NULL |
| `extracted_data_json` | TEXT | NOT NULL |
| `validation_json` | TEXT | NULL |
| `created_at` | TEXT | NOT NULL |

A session can have at most one persisted extraction result in WP2. Extraction is valid only for an approved session.

### 2.5 `observations`

| Column | Type | Constraints |
|---|---|---|
| `observation_id` | TEXT | PK |
| `result_id` | TEXT | FK → `extraction_results.result_id`, NOT NULL |
| `session_id` | TEXT | FK → `sessions.session_id`, NOT NULL |
| `user_id` | TEXT | FK → `users.user_id`, NOT NULL |
| `trait_id` | TEXT | NOT NULL |
| `trait_name` | TEXT | NOT NULL |
| `score` | REAL | NOT NULL; 0.0–1.0 |
| `confidence` | REAL | NOT NULL; 0.0–1.0 |
| `evidence_json` | TEXT | NOT NULL |
| `source` | TEXT | NOT NULL |
| `situational_factor` | TEXT | NULL |
| `created_at` | TEXT | NOT NULL |

Observations are the historical/source-of-truth trait evidence. They are append-only: WP2 exposes insert/read operations only; there are deliberately no update/delete repository methods.

### 2.6 `trait_scores`

`TraitScore` is a computed representation, not the historical source of truth. It may be refreshed by the aggregation layer from observations.

| Column | Type | Constraints |
|---|---|---|
| `user_id` | TEXT | FK → `users.user_id`, NOT NULL |
| `trait_id` | TEXT | NOT NULL |
| `trait_name` | TEXT | NOT NULL |
| `score` | REAL | NOT NULL; 0.0–1.0 |
| `observation_count` | INTEGER | NOT NULL; >= 0 |
| `computed_at` | TEXT | NOT NULL |

Primary key: (`user_id`, `trait_id`).

This table is replaceable/recomputable. Deleting a trait score must never delete its observations.

## 3. Relationships

```text
users
  1
  |
  N
sessions
  |   |  \ 0..1
  |     |    extraction_results
  |
  N
chat_messages

extraction_results
  1
  |
  N
observations

users
  1
  |
  N
trait_scores
```

Conceptually:

- one user has many sessions;
- one session has many chat messages;
- one session has zero or one extraction result;
- one extraction result has many observations;
- one user has many computed trait scores.

`TraitObservation` is the historical/source-of-truth layer. `TraitScore` is derived/computed.

## 4. Session lifecycle invariants

### Pending

A pending session may have chat messages, but:

- no extraction result;
- no observations;
- no trait score is created by the storage layer.

### Rejected

A rejected session retains its chat history, but:

- no extraction result;
- no observations.

### Approved

An approved session may have:

- one extraction result;
- zero or more observations produced from that result.

The repository rejects extraction/observation writes when the session is not approved.

## 5. User isolation

Every repository method takes `user_id` as its first argument.

Queries that access user-owned data include the user predicate explicitly. Child records are checked through both their direct `user_id` and their parent relationship where appropriate.

A caller cannot read another user's session, messages, extraction results, observations, or trait scores by knowing only the child ID.

## 6. Account deletion

`delete_account(user_id)` removes all data owned by that user and only that user.

Foreign keys are enabled. The schema uses cascading relationships from `users` to user-owned records and from sessions/results to their children. The repository deletes the user row only after verifying that the transaction is scoped to the requested user.

## 7. SQLite rules

- Python standard library `sqlite3` only.
- Foreign keys enabled with `PRAGMA foreign_keys = ON`.
- Parameterized SQL only.
- Supports `:memory:` and file database paths.
- Explicit transaction boundaries are used for multi-row writes.
- Indexes are added for user/session/result lookup paths.

## 8. Repository contract

The implementation exposes these logical operations:

### Users
- `create_user(user_id, created_at)`
- `user_exists(user_id)`
- `delete_account(user_id)`

### Sessions
- `create_session(user_id, ...)`
- `get_session(user_id, session_id)`
- `list_sessions(user_id)`
- `update_session_status(user_id, session_id, status, approval_date)`
- `delete_session(user_id, session_id)` (session deletion is allowed; observation deletion is not)

### Chat messages
- `append_chat_message(user_id, session_id, ...)`
- `list_chat_messages(user_id, session_id)`

### Extraction
- `save_extraction_result(user_id, session_id, ...)`
- `get_extraction_result(user_id, session_id)`

### Observations
- `append_observation(user_id, session_id, ...)`
- `list_observations(user_id, session_id)`
- `list_user_observations(user_id)`

There are intentionally no `update_observation` or `delete_observation` methods.

### Trait scores
- `upsert_trait_score(user_id, trait_id, ...)`
- `list_trait_scores(user_id)`

## 9. Validation and integrity

The storage layer validates:

- session status is one of `pending`, `rejected`, `approved`;
- message role is one of `user`, `system`;
- extraction status is non-empty;
- scores and confidence values are within `[0, 1]`;
- observations reference an approved session and an existing extraction result;
- extraction results are unique per session.

## 10. Test coverage

The contract tests cover:

1. memory database creation;
2. file database creation;
3. foreign keys;
4. user isolation;
5. session lifecycle;
6. pending/rejected extraction rejection;
7. approved extraction and observation insertion;
8. observation append-only behavior;
9. extraction provenance metadata;
10. separate decision/approval dates;
11. full account deletion;
12. computed trait-score persistence;
13. parameterized inputs containing SQL-like text.