# Decision Mirror — Task 5: Profile Engine and Foundations

Status:
 Draft v0.1, proposed, pending team lead approval ·
Owner:
 Zeyad (team lead) ·
Date:
 21 Nov 2026
Covers:
 Stages A and B of
Decision Mirror Phase 1 Build Plan
 (shared models, configuration, storage, synthetic data, aggregation,
T06, session state machine, quiz module), plus closing the open Task 4 conditions.
Target location in repo:
docs/tasks/task-5-profile-engine/00_task5_brief.md
1. Why we are doing this task
Task 4 proved the first risky claim of the project: an LLM can turn a short decision text into structured trait observations (score or null,
confidence, evidence quotes, situational factor) under a frozen contract. But an extraction result is only one observation about one
decision. Nothing in the repository yet
turns many observations into a profile
.
Chapter 3 states that
the history is the source of truth and the current scores and T06 are computed from it
. Task 5 builds that part. It is
the deterministic core of the product:
It needs
no LLM and no API calls
, so every behaviour can be tested
exactly
, with hand-computed expected values, and costs
nothing to run.
Every later module reads from it: the Elicitation and Advisor roles read the profile, Retrieval reads the stored decisions, the API
wraps it, and the dashboard displays it.
Building it first means the LLM roles (Task 6) and the API (Task 7) are built on shapes and rules that are already tested, not on
guesses.
Task 5 also sets up the
team's engineering workflow
 (one branch per person, pull requests only, no direct pushes to
main
) that every
later task will use.
2. Objectives
ID
Objective
How we know it is met
T5-
O1
Every module speaks the same typed shapes, built from
the frozen extraction contract v1.0
The 6 valid fixtures in
schemas/
examples/
valid/
 load into the shared
models; the invalid fixtures are rejected
T5-
O2
Every tunable value lives in one configuration object
No threshold, weight or tier cut-off is hard-coded anywhere else
(checked in review)
T5-
O3
Storage keeps an append-only history, scoped per user,
with full account deletion
Storage contract tests pass on an in-memory and a file database
T5-
O4
Current trait scores and T06 are computed by pure,
deterministic functions
Hand-computed oracle cases pass; recomputing from the same history
gives the same result
T5-
O5
The quiz can be served without leaking the answer key and
scored without an LLM
The served quiz file contains no gold fields; all 125 answer records map to
their anchor values
T5-
O6
All test data is clearly synthetic and labelled
Every synthetic record carries
synthetic: true
; the same seed gives
byte-identical output
T5-
O7
Nothing frozen in Task 4 is changed
Hashes in
TASK4_MANIFEST.json
 still match after every merge
T5-
O8
The Task 4 open conditions are closed
Human review file completed; approval line in
06_
evaluation_
report.md
filled by the team lead
3. Scope
In scope:
 everything in sections 6.1–6.8 below.
Out of scope (later tasks):
 the Elicitation, Advisor and Profile-describer LLM roles (Task 6), retrieval, the approval pipeline that calls
extraction, the backend API and authentication, the frontend, Docker.
Do not start any of these.
 Do not call the real LLM API anywhere
in Task 5. Tests use fakes only.

4. Deliverables at a glance
WP
Owner
Deliverable
Depends on
Wave
WP1
Habiba Ahmed Abdo
Shared domain models + configuration
none
1
WP2
Ahmed Osama Ahmed
Storage layer (interfaces + SQLite)
WP1 (code), design doc
first
1 (design), 2 (code)
WP3
Mohamed Abdelhakam
Abdelaal
Aggregation policy + oracle fixtures + aggregation
engine
WP1 (code only)
1 (policy), 2 (code)
WP4
Zeyad
T06 policy + Omar reference scenario source + T06
engine + Gate 1 test
WP1, WP3
1 (policy), 2 (code)
WP5
Mohamed Ali Alaily
Session state machine + reminder rule + Task 4 human
review
WP1 (code only)
1 (review), 2 (code)
WP6
Shams Amr Saber Zaki
Quiz module (client-safe content, server-side key,
scoring)
WP1
1 (content), 2
(scoring)
WP7
Mohamed Esawy Elmeshad
Security and privacy baseline + two-user isolation tests
WP2 (tests only)
1 (docs), 2 (tests)
WP8
Roney Maged Morkes
Synthetic data generator + labelling guard
WP1, Omar source from
WP4
2
Waves.
 Wave 1 starts now: WP1 is the only code that blocks others, so it is merged first, and everyone else does their documents, designs
and fixtures while it is built. Wave 2 starts when WP1 is merged to
main
.
Gate 1
 (section 8) closes the task.
5. Team workflow (mandatory)
5.1 Accounts and branches
Zeyad adds each member as a collaborator on
github.com/z3yad30/Decision-Mirror
 using the GitHub usernames below, and turns on
branch protection for
main
 (pull request required, 1 approval, no direct pushes, no force pushes).
Member
GitHub username
WP
Habiba Ahmed Abdo
@____
WP1
Ahmed Osama Ahmed
@____
WP2
Mohamed Abdelhakam Abdelaal
@____
WP3
Zeyad
z3yad30
WP4
Mohamed Ali Alaily
@____
WP5
Shams Amr Saber Zaki
@____
WP6
Mohamed Esawy Elmeshad
@____
WP7
Roney Maged Morkes
@____
WP8
Rules
1.
Each person works only on their own branch
, named
<github-username>/t5-<wp>-<short-name>
, for example
habiba-dev/t5-
wp1-models-config
. If a WP has a wave 1 part and a wave 2 part, use one branch per wave: add a
-w1
 or
-w2
 suffix.
2.
You push only your own branch.
 Never push to
main
. Never force-push. Never push to someone else's branch. Never rebase a
branch someone else has pulled.
3.
Start each wave from a fresh
main
:
4.
Commit small and often, with messages like
WP3: add aggregation oracle fixtures
. Push with
git push -u origin <your-
branch>
.
5.
When your "done when" list is complete, open a
pull request into
main
. Zeyad merges; nobody merges their own PR.
6.
To pick up changes from
main
 while you work, run
git merge main
into your own branch
, then resolve conflicts there.
git switch main
git pull
git switch -c <username>/t5-<wp>-<short-name>

5.2 Files you may and may not touch
Touch only the files listed in your WP.
 If you need a change in someone else's file, write it in your PR description and ask the
owner.
Frozen, never edit:
 everything under
schemas/
 (contract v1.0),
prompts/extraction/
,
data/gold/
,
data/processed/eval_set_v1.json
 and
split_v1.json
,
evaluation/
,
src/decision_mirror/extraction/
, and all Task 4 docs.
Zeyad checks
TASK4_MANIFEST.json
 hashes before each merge.
Shared files, do not edit:
requirements.txt
,
README.md
,
file_structure.txt
. Several branches editing them causes merge
conflicts. Instead, put in your PR description (a) any new dependency you need, (b) a 3–5 line README snippet for your part.
Zeyad consolidates them and regenerates
file_structure.txt
 after merging.
One exception:
 WP1 adds
pydantic
 to
requirements.txt
, pinned. No other new dependency is approved. Use the standard library otherwise.
Put your working notes in
docs/tasks/task-5-profile-engine/notes/wp<N>_<name>.md
 (your own file, no conflicts).
5.3 Pull request checklist (copy into every PR)
Virtual environment active;
pytest -q
 passes locally
No real API call anywhere; no key, token or password in any file (
.env
 stays ignored)
No file from the frozen list changed
Every "done when" item for my WP is ticked, with the test name that proves it
PR description contains the README snippet and any dependency request
Synthetic data, where used, is labelled
synthetic: true
5.4 Peer review pairs
Every PR gets Zeyad
and
 one peer. Peer reads the code and the tests, and runs the tests on their machine.
Author
Peer reviewer
Habiba (WP1)
Mohamed Ali
Ahmed Osama (WP2)
Habiba
Mohamed Abdelhakam (WP3)
Zeyad
Zeyad (WP4)
Mohamed Abdelhakam
Mohamed Ali (WP5)
Shams
Shams (WP6)
Ahmed Osama
Mohamed Esawy (WP7)
Roney
Roney (WP8)
Mohamed Esawy
5.5 Environment
Use the project virtual environment for everything. Windows PowerShell:
.venv\Scripts\Activate.ps1
; macOS/Linux:
source

.venv/bin/activate
. Install with
pip install -r requirements.txt
. Never install packages globally.
6. Work packages
6.1 WP1 — Shared domain models and configuration · Habiba Ahmed Abdo
Why:
 every module (storage, aggregation, T06, quiz, sessions, later the API) must read and write the same shapes. If each person
invents their own, nothing connects. This is the one task that blocks the others, so it goes first and fast.
Branch:
<username>/t5-wp1-models-config
 ·
Depends on:
 nothing ·
Wave:
 1
Files to create
1.
src/decision_mirror/common/models.py
 — typed models (use
pydantic
,
extra="forbid"
 everywhere):
TraitId
 enum
T01
–
T06
,
Source
 enum (
quiz
,
decision
),
SessionStatus
 enum (
pending
,
approved
,
rejected
),
SituationalCategory
 enum with the exact 8 categories from
schemas/extraction_output.schema.json
.
SituationalFactor
 (
category
,
description
).
TraitObservation
:
trait_id
,
score
 (float 0–1 or
None
),
confidence
 (0–1),
evidence
 (list of strings),
situational_factor
(or
None
),
context_notes
,
source
. Validators mirror the contract's semantic rules: a
None
 score forces
confidence == 0.0
and
evidence == []
; a non-null score requires at least one evidence item.
ExtractionOutput
 — exactly the LLM output object of contract v1.0 (
decision_id
,
extraction_status
, six traits in order).
ExtractionResult
 — the pipeline envelope from
schemas/extraction_result.schema.json
 (adds
model_version
,
prompt_version
,
prompt_sha256
,
error
,
validation
).
DecisionRecord
:
decision_id
,
user_id
,
session_id
,
decision_text
,
decision_date
,
approval_date
 (nullable),
status
,
observations
,
prompt_version
,
prompt_sha256
,
model_version
,
advisor_top_choice_approved
 (nullable bool, reserved for
later study of confirmation bias),
synthetic
 (bool, default
False
).
The decision date and the approval date are
separate fields
. A late approval must never change the decision date.

2.
src/decision_mirror/common/config.py
 — one
Settings
 object. Defaults below are
proposed starting values
, each documented
in a comment and marked
PROPOSED
. Each can be overridden by an environment variable with the prefix
DM_
 (for example
DM_REMINDER_DAYS=7
).
Setting
Default
Note
t06_min_usable
4
nothing shown below this
t06_strong_at
8
moderate from 4–7, strong from 8
reminder_days
7
pending decision reminder
situational_weight
0.5
weight multiplier for a decision with a situational factor
quiz_weight
0.5
weight multiplier for quiz observations
quiz_confidence
0.30
fixed low confidence for quiz observations
recency_
half_
life_
days
None
no recency decay in the first version
shift_window
3
placeholder
, to be calibrated in WP3/WP4
shift_threshold
0.15
placeholder
, to be calibrated in WP3/WP4
3.
tests/test_models.py
 — load all 6 files in
schemas/examples/valid/
 into
ExtractionOutput
 and assert that serializing them back
gives the same JSON. Assert that every file in
schemas/examples/invalid/
 is rejected (a file whose body is not JSON counts as
rejected at parse time). Add tests for each semantic validator (null score with non-zero confidence, non-null score without
evidence, unknown field, wrong
trait_id
).
4.
tests/test_config.py
 — defaults load; an environment override changes the value; an invalid override (negative days, weight
above 1) raises.
5.
Add
pydantic
 to
requirements.txt
, pinned to the installed version (the only dependency change in Task 5).
6.
docs/tasks/task-5-profile-engine/notes/wp1_models_config.md
 — one page: the model list, one example of each, and the settings
table.
Done when:
 the six valid fixtures round-trip unchanged; every invalid fixture is rejected; the settings load, override and validate;
decision_date
 and
approval_date
 are separate;
pytest -q
 is green; no setting value is hard-coded outside
config.py
.
Do not:
 change anything in
schemas/
 or
src/decision_mirror/extraction/
. If the contract and a model disagree, the contract wins; tell
Zeyad.
6.2 WP2 — Storage layer · Ahmed Osama Ahmed
Why:
 the profile must survive restarts, belong to exactly one user, and be tamper-evident. The history is the source of truth; scores are
recomputed from it. Chapter 3 requires: append-only observations, every query scoped to a user, and the ability to delete an account
completely (FR-07, FR-18, NFR-03, NFR-04).
Branch:
<username>/t5-wp2-storage-w1
 (design) and
-w2
 (code) ·
Depends on:
 WP1 merged, for the code part ·
Wave:
 1 design, 2 code
Wave 1 — design (no code)
docs/tasks/task-5-profile-engine/notes/wp2_storage_design.md
: the tables and columns (users, sessions, chat_messages,
observations, extraction_results), keys and foreign keys, the list of repository methods with signatures, how append-only is
enforced, how account deletion works, and what is stored with each extraction result (prompt version, prompt hash, model
version). Zeyad and Habiba review it before you start coding. Follow the entity diagram in Chapter 3 §3.3. Rules that must appear:
Only approved sessions have an extraction result and observations. A rejected session keeps its chat messages and nothing
else. A pending session has no extraction.
Quiz observations are stored with
source = quiz
.
Observations are never updated or deleted, except when the whole user is deleted.
Wave 2 — code
1.
src/decision_mirror/storage/interfaces.py
 — abstract repository interfaces (
UserRepository
,
SessionRepository
,
ChatMessageRepository
,
ObservationRepository
,
ExtractionResultRepository
).
Every method takes
user_id
 as the first
argument.
ObservationRepository
 has
append
 and read methods only: no update and no delete method exists.
2.
src/decision_mirror/storage/sqlite_store.py
 — implementation with the standard library
sqlite3
 (no new dependency).
Requirements:
Parameterized queries only; never build SQL with string formatting.
Foreign keys on.
Append-only enforced
in the database as well as in Python
 (for example
BEFORE UPDATE
 and
BEFORE DELETE
 triggers on
the observations table that abort, with a carefully written exception for deleting the owning user; verify with a test that the
exception works and nothing else can delete).
delete_user(user_id)
 removes every row of that user in every table.
The same class works for
":memory:"
 and for a file path.
Dates stored as ISO-8601 UTC strings.

3.
tests/test_storage_contract.py
 — parametrized to run the
same tests
 on an in-memory database and on a temporary file
database:
an attempt to update or delete a stored observation fails;
reading with another user's id returns nothing;
delete_user
 leaves zero rows for that user in every table and does not touch other users;
a rejected session keeps chat messages and has no observations; a pending session has no extraction result;
decision_date
 and
approval_date
 are stored separately and a late approval does not change
decision_date
;
prompt version, prompt hash and model version round-trip with each extraction result;
a file database reopened in a new connection returns the same data.
Done when:
 the contract tests pass on both database types; any modification of a stored observation fails; every method requires a user
id; account deletion is complete.
Do not:
 add SQLAlchemy or any other library; write HTTP or API code; call any LLM.
6.3 WP3 — Aggregation policy, oracle fixtures, aggregation engine · Mohamed Abdelhakam Abdelaal
Why:
 this is the rule that decides what the system believes about a person. It must be written down and checked by hand
before
 it is
coded, so that the tests check the rule, not the code against itself. The Task 4 handoff requires every aggregation policy to be
documented and validated before use. You are the Data Science owner of this rule.
Branch:
<username>/t5-wp3-aggregation-w1
 (policy + fixtures) and
-w2
 (code) ·
Depends on:
 WP1 merged, for the code part ·
Wave:
 1
policy, 2 code
Wave 1 — policy and fixtures (no code)
1.
docs/design/aggregation_policy.md
, labelled
PROPOSED
. It must specify, with formulas:
Input: the observation history of one user for one trait.
Null scores contribute nothing
 and are never replaced by a midpoint such as 0.5. If a trait has no non-null observation, the
output is
score = null
,
confidence = 0.0
, status
insufficient
.
Weight of an observation
 =
confidence × source_weight × situational_weight
, where
source_weight
 is
quiz_weight
 for
quiz and 1 for decisions, and
situational_weight
 applies whenever
situational_factor
 is not null.
Do not use the
situational factor's category
 to decide the weight, because category agreement was weak in Task 4 evaluation. No recency
decay in the first version, but state where it would plug in.
Score
 = weighted mean of non-null scores.
Confidence rule:
 propose a formula and justify it. Baseline you may start from:
confidence = W / (W + k)
 where
W
 is the
sum of weights and
k
 is a constant. It must satisfy these properties (write each as a test case): (a) no data gives 0.0; (b) a
quiz-only profile has lower confidence than a profile with 3 or more decisions of moderate confidence; (c) adding a
consistent observation never lowers confidence; (d) confidence is always in [0, 1].
T06 is
not
 aggregated here (it is computed in WP4). Observations for T06 are ignored by this engine.
What happens when quiz and decision observations disagree (the weighted mean handles it; state that no special rule
exists).
2.
tests/fixtures/aggregation_oracle.json
 — at least
12 hand-computed cases
. Each case has
name
,
settings
 (if not default),
observations
 (inputs),
expected
 (score, confidence, status) and a
working
 field showing the arithmetic step by step. Cover:
empty history; quiz only; one decision; several decisions; a null in the middle; all nulls; one situational decision at half weight; a
situational decision with an unusual category (must get the same weight as any other); conflicting scores; extreme weights; quiz
plus decisions; a changed
quiz_weight
 giving a different result. Compute them by hand (or a calculator)
independently of any
code
.
3.
docs/tasks/task-5-profile-engine/notes/wp3_open_points.md
 — list any rule you could not settle, with your recommended
default. Zeyad decides.
Wave 2 — code
1.
src/decision_mirror/profiling/aggregation.py
:
compute_trait_state(observations, settings) -> TraitState
 and
compute_profile(observations, settings) ->

dict[TraitId, TraitState]
 (T01–T05 only).
TraitState
 has
score
,
confidence
,
status
,
n_observations_used
,
n_quiz
,
n_decision
.
Pure functions:
 they never modify their input, never read the clock, never touch storage or the network.
2.
tests/test_aggregation.py
 — runs every case in
aggregation_oracle.json
 (tolerance 1e-9); a test that the input list is
unchanged (compare with a deep copy); determinism (same input twice gives the same output); a test that changing
quiz_weight
 or
situational_weight
 in settings changes the result; the four confidence properties above as property-style tests.
Done when:
 the policy document is approved by Zeyad; every oracle case passes; the four confidence properties hold; functions are
pure; no weight or threshold is hard-coded in the module.
6.4 WP4 — T06 policy, reference scenario, T06 engine, Gate 1 · Zeyad (team lead)
Why:
 T06 Self-Consistency is computed from history, never extracted by the LLM (Ontology and Chapter 1, FR-20). It is the feature that
distinguishes Decision Mirror from a quiz. The reference scenario (Omar) is the hand-checkable example the whole project uses for
tests and the demo.
Branch:
z3yad30/t5-wp4-t06-w1
 and
-w2
 ·
Depends on:
 WP1 ·
Wave:
 1 policy, 2 code
Wave 1

1.
docs/tasks/task-5-profile-engine/source/omar_reference_scenario.md
 — the Omar scenario as a table: nine labelled synthetic
decisions with dates, T01–T05 scores and confidences, which decisions carry a situational factor, and the hand-computed T06
values at 4 and 9 decisions. This file is the source of truth for WP8 and for the Gate 1 test.
Everyone blocked on it (WP8) waits for
it, so it goes first.
2.
docs/design/t06_policy.md
 — the T06 rule: per trait, using only
approved, scored (non-null for that trait), non-situational
decisions;
value = 1 − 2 × population standard deviation
 of those scores; tiers: below
t06_min_usable
 (4) nothing is shown, 4–
7 moderate, 8 or more strong;
shift flag
 fires when the mean of the last
shift_window
 decisions differs from the mean of the
earlier ones by at least
shift_threshold
. The window and threshold are calibrated from synthetic cases, not guessed; the
calibration is written in this document.
Wave 2
1.
src/decision_mirror/profiling/self_consistency.py
 —
compute_t06(decisions, settings) -> dict[TraitId, T06State]
 (for
T01–T05), with
value
,
tier
 (
hidden | moderate | strong
),
usable_count
,
shift_flag
. Pure function.
2.
tests/test_self_consistency.py
 — below 4 returns hidden; the tier switches exactly at 4 and 8; a situational decision is excluded;
a pending or rejected decision is excluded; a null for that trait is excluded; a shift is flagged and a stable history is not; the Omar
scenario gives about 0.90 at the first checkpoint and about 0.74 at the second (exact values from the scenario file).
3.
tests/test_gate1_profile_engine.py
 — the Gate 1 integration test (section 8).
4.
Lead duties: merge PRs in order, check
TASK4_MANIFEST.json
 hashes, consolidate README and
requirements.txt
, regenerate
file_structure.txt
.
Done when:
 all T06 tests pass and the policy and scenario documents exist and are consistent with each other.
6.5 WP5 — Session state machine + Task 4 human review · Mohamed Ali Alaily
Why:
 Chapter 1 defines the decision lifecycle: pending, approved, rejected; only approval changes the profile; a pending decision is
reminded after 7 days. This must be a small, strict, testable rule, with no database or HTTP, so that the API and the UI cannot get it
wrong. Separately, the Task 4 report still says
pending
 because the human cross-review of flagged items (your original Task 4
deliverable) was never completed.
Branch:
<username>/t5-wp5-sessions-w1
 (human review) and
-w2
 (code) ·
Depends on:
 WP1 merged, for the code part ·
Wave:
 1
review, 2 code
Wave 1 — human review of Task 4 (no code)
In
human_review/
 (created by the Task 4 evaluation), open the sampled
needs_manual_review
 items. For each one, read the input,
the model's score and its evidence quotes, and record a verdict:
supported
,
partially supported
 or
not supported
, plus a
one-
line reason
. Judge whether the quote really justifies the score, not whether the score matches gold.
Shams does an
independent second pass on the same items
 without seeing your verdicts (see WP6). Then you two compare
them and list disagreements with a short note.
Output: the completed review file and
docs/tasks/task-5-profile-engine/notes/wp5_human_review_summary.md
 with counts per
verdict and any pattern you saw (for example, evidence that is quoted but does not support the score). Do
not
 edit the Task 4
report; Zeyad updates it.
Wave 2 — code
1.
src/decision_mirror/sessions/__init__.py
 and
src/decision_mirror/sessions/state.py
 (new package; follow the
__init__.py
convention of the others). Pure functions, no database, no HTTP,
no
datetime.now()
 inside
: the current time is always passed in.
ALLOWED_TRANSITIONS
:
pending → approved
,
pending → rejected
. Approved and rejected are final.
apply_event(session, event, now) -> session
:
approve
 sets
approval_date = now
 and
leaves
decision_date
 unchanged
;
reject
 sets the status and saves nothing else. Any other transition raises
InvalidTransition
.
is_reminder_due(session, now, settings) -> bool
: true only for a pending session whose age is
at least
reminder_days
. It
is true exactly at the boundary and false one second before.
2.
tests/test_session_state.py
 — every allowed transition passes and
every other combination raises
; the reminder boundary at
exactly 7 days, just before and just after; a late approval keeps its original
decision_date
; a changed
reminder_days
 setting moves
the boundary; reminders are never due for approved or rejected sessions.
Done when:
 the human review is complete with a summary; every transition rule and the reminder boundary are tested; no clock or I/O
in the module.
6.6 WP6 — Quiz module · Shams Amr Saber Zaki
Why:
 the quiz sets the initial trait values at sign-up (FR-02, FR-03). The 25 scenarios and their gold anchors already exist from Task 3, so
the product quiz needs
no LLM
: scoring is a lookup of fixed anchors. The critical rule is that the
answer key must never reach the
client
.
Branch:
<username>/t5-wp6-quiz-w1
 and
-w2
 ·
Depends on:
 WP1 merged, for the scoring part ·
Wave:
 1 content, 2 scoring
Wave 1 — content and key
1.
scripts/build_quiz_content.py
 — reads
data/gold/quiz_gold_v1.0.json
 (read-only; never write to it) and writes two files,
deterministically:
data/processed/quiz_content_v1.json
 —
client-safe
: per question
question_id
,
scenario
, and its 5 options with
option_id
 and
text
.
No
trait_id
, gold value, evidence, confidence or any other gold field. Check whether the option
order correlates with the gold value; if it does (for example A is always the lowest), shuffle the display order with a fixed seed
and record the order, so that position does not reveal the key.

data/processed/quiz_key_v1.json
 —
server-side only
: for each
(question_id, option_id)
 the target
trait_id
 and the
anchor value. This file is never served.
Record the SHA-256 of the gold file and both outputs in
data/processed/quiz_MANIFEST.json
.
2.
tests/test_quiz_content.py
 — the content file has 25 questions × 5 options;
no key named
trait_id
,
gold*
,
evidence
,
confidence
 or
value
 appears anywhere in the content file
; the key file covers all 125 records and its values equal the gold values
exactly; the build is deterministic (run twice, same hashes).
3.
Independent second pass of the Task 4 human review (see WP5) in
human_review/
: same items, your own verdicts, before you see
Mohamed Ali's.
Wave 2 — scoring
1.
src/decision_mirror/quiz/content.py
 —
load_quiz()
 returns the client-safe questions only.
2.
src/decision_mirror/quiz/scoring.py
 —
score_answers(answers: dict[question_id, option_id]) -> list[TraitObservation]
.
One observation per answered question: the target trait gets the anchor score,
confidence = settings.quiz_confidence
,
source =

quiz
,
evidence
 contains the selected option text, and no other trait is scored. Unknown question or option ids raise a clear error.
T06 is never produced. The key is loaded from the server-side key file only.
3.
tests/test_quiz_scoring.py
 — all 125 answer records map to their anchor values; every observation is marked
source = quiz
and carries the configured confidence; an unknown id is rejected; a partial answer set is handled as documented; a changed
quiz_confidence
 changes the output.
Done when:
 the served file has no gold fields; all 125 records map to the exact gold values; scoring needs no LLM; the key file is not
importable by any client-facing function.
6.7 WP7 — Security and privacy baseline · Mohamed Esawy Elmeshad
Why:
 the profile contains personal decision text and psychological traits. NFR-03, NFR-04 and NFR-05 must be built in from the
storage layer upward, not added at the end. Decision text is also sent to an external LLM provider, and the user must be told (Chapter 3,
§3.6).
Branch:
<username>/t5-wp7-security-w1
 and
-w2
 ·
Depends on:
 WP2 merged, for the isolation tests ·
Wave:
 1 docs, 2 tests
Wave 1 — documents and a secret scanner
1.
docs/design/security_baseline_stage_ab.md
 — a threat table for the Stage A/B components: cross-user data access, SQL
injection, tampering with the append-only history, leaked keys in the repository or in logs, mislabelled synthetic data shown as
real, incomplete account deletion, and an unfrozen quiz key reaching the client. For each: the control, the requirement it supports
(NFR-03/04/05), how it will be tested, and the OWASP reference (Top 10 and LLM Top 10 where relevant).
2.
docs/design/privacy_notice_draft.md
 — the plain-language sign-up notice, about one page, labelled
DRAFT for supervisor
review
. It states: what is collected (quiz answers, decision text, chats, derived scores), that decision text is sent to an external LLM
provider to extract traits, who can see the data (only the user), how long it is kept, and how the user deletes everything.
3.
scripts/check_secrets.py
 — scans the tracked files for secrets: Groq-style keys (prefix
gsk_
),
GROQ_API_KEY=
 lines with a non-
empty value, private keys, and a tracked
.env
 file. Exit code 1 if anything is found, with file and line (never print the secret itself).
4.
tests/test_security_baseline.py
 — runs the scanner on the repository (must pass); asserts
.env
 is in
.gitignore
; asserts
.env.example
 has an empty
GROQ_API_KEY=
.
Wave 2 — isolation tests (after WP2 is merged)
1.
tests/test_user_isolation.py
 — create two users (A and B) with sessions, chats, observations and extraction results in the
storage layer. For
every repository method
, assert that user B can never read, list, update or delete user A's data, and that deleting
user A leaves B's data intact. Add a test that a stored text containing SQL-like content (
'; DROP TABLE users; --
) is stored as plain
text and breaks nothing.
2.
A static test: the storage module contains no SQL built with f-strings or string concatenation (a simple source scan is enough).
3.
Report any weakness you find to Ahmed Osama and Zeyad in the PR;
do not edit
storage/
 yourself
.
Done when:
 the security and privacy documents exist; the scanner and baseline tests pass; the two-user isolation suite passes against
the real storage layer.
6.8 WP8 — Synthetic data generator · Roney Maged Morkes
Why:
 tests, demos and the future dashboard need realistic histories, and we have no real users yet. Chapter 1 and 3 require that
synthetic data is
labelled as synthetic everywhere
, so a demo can never present it as measured. The Omar reference scenario must be
reproducible so that WP4 and the Gate 1 test can check T06 against hand-computed values.
Branch:
<username>/t5-wp8-synthetic-data
 ·
Depends on:
 WP1 merged and Zeyad's
omar_reference_scenario.md
 (WP4, wave 1) ·
Wave:
 2
Files to create
1.
src/decision_mirror/common/synthetic.py
 — the generator logic and the guard:
build_synthetic_users(seed) -> list[dict]
 returning labelled synthetic users with approved, pending and rejected
decisions.
refuse_unlabelled(records)
 raises an error if any record that should be synthetic lacks
synthetic: true
 and a
synthetic_label
 string. Demos and later UI code use it.
2.
scripts/make_synthetic_users.py
 — a thin command-line wrapper:
python scripts/make_synthetic_users.py --seed 42
 writes
data/processed/synthetic_users_v1.json
 and its SHA-256.
3.
The generated users (ids prefixed
SYN_
, every record
synthetic: true
):

a
quiz-only
 user (25 quiz observations, no decisions);
a user with
3
 approved decisions (below the T06 minimum);
a user with
5
 approved decisions (moderate T06 tier);
the
Omar
 user with
9
 approved decisions, reproducing the values in
omar_reference_scenario.md
 exactly, including the
shift;
a user with a
mix of approved, pending and rejected
 decisions;
a user with one
situational-factor
 decision. Decision texts are short, generic, and clearly invented;
do not copy any text
from the quiz, the ontology's 20 annotated decisions or the edge-case set.
4.
tests/test_synthetic.py
 — the same seed gives byte-identical output (compare hashes); every record is flagged;
refuse_unlabelled
 raises on a stripped record; the Omar user's stored scores equal the scenario file exactly; counts of decisions
per user are as listed; decision dates are in the past and in order.
Done when:
 the output is deterministic and fully labelled; the Omar user matches the scenario file; the guard works.
7. Open decisions (defaults are proposals)
#
Decision
Owner
Default if not decided
1
Aggregation weights (situational, quiz weight, quiz
confidence), recency
Zeyad, advised by
WP3
Values in section 6.1; no recency decay
2
T06: population or sample standard deviation; shift window
and threshold
Zeyad
Population SD; window and threshold calibrated on
synthetic cases
3
Quiz scoring: fixed anchors or LLM extraction
Zeyad
Fixed anchors
4
New dependencies
Zeyad
Only
pydantic
; storage uses the standard library
5
Task 4 readiness thresholds (approval line in the report is
blank)
Zeyad
Approve, or change before any new evaluation
8. Gate 1 and acceptance
Task 5 is closed when
all
 of these hold on
main
:
1.
All eight WP "done when" lists are satisfied and every PR is merged by Zeyad after review.
2.
pytest -q
 passes on a
fresh clone with a fresh virtual environment
 (
pip install -r requirements.txt
).
3.
tests/test_gate1_profile_engine.py
 passes: the Omar synthetic user is loaded from the generator, written to the SQLite store,
read back, aggregated into current trait scores, and T06 is computed; the T06 values equal the hand-computed ones in the
scenario file; the same run on an in-memory and a file database gives identical results.
4.
No test makes a real API call, and the secret scanner passes.
5.
TASK4_MANIFEST.json
 hashes still match (nothing frozen was edited).
6.
README,
requirements.txt
 and
file_structure.txt
 are updated by Zeyad from the PR snippets.
7.
The Task 4 human review is complete and the team lead's approval line in
06_evaluation_report.md
 is filled.
What follows Task 5 (not part of it):
 Task 6 builds the LLM roles (role client and fake client, role prompt registry, retrieval, Elicitation,
Advisor, Profile describer) and the approval pipeline; Task 7 the command-line slice and the backend API; then the frontend.
