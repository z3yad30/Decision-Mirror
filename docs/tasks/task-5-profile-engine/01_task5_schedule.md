# Decision Mirror — Task 5 Schedule and Deadlines

Start:
 Wednesday 25 November 2026 ·
End (Gate 1):
 Friday 4 December 2026 ·
Owner:
 Zeyad
Target location in repo:
docs/tasks/task-5-profile-engine/01_task5_schedule.md
 Read
00_task5_brief.md
 first. This file only says
who delivers what, and by when
.
Read this first (60 seconds)
What we build:
 the part of Decision Mirror that turns many single-decision observations into one user profile. No LLM, no API
calls. Everything is tested with numbers we calculated by hand.
Why a schedule with waves:
 one task (WP1, Habiba) blocks the code of the others. While it is built, everyone else works on
documents, designs and test data. When it is merged, everybody codes.
"Delivered" means:
 a pull request is
opened
 from your own branch, the PR checklist is ticked, and tests pass locally. Merging is
done by Zeyad after review.
Reviews:
 the peer reviewer named in the brief reviews within
24 hours
 of the PR being opened. Zeyad reviews after the peer.
If you are blocked or late:
 write in the team group
the same day
, not on the deadline. Say what blocks you and what you need.
Timeline at a glance
Day
Date
What happens
1
Wed 25 Nov
Kickoff. Branches created. Habiba starts WP1.
2
Thu 26 Nov
WP1 PR opened.
 Zeyad's Omar scenario PR opened.
3
Fri 27 Nov
WP1 merged
 (Wave 2 code can start). Ahmed's storage design PR opened.
4
Sat 28 Nov
Wave 1 documents due.
 15-minute team check-in.
5
Sun 29 Nov
Human-review comparison due. Wave 2 coding.
6
Mon 30 Nov
Wave 2 coding.
7
Tue 1 Dec
Storage, state machine and quiz-scoring PRs opened.
8
Wed 2 Dec
Aggregation, T06 and synthetic-data PRs opened. Storage merged.
9
Thu 3 Dec
Isolation tests PR opened.
Last day to open any PR.
10
Fri 4 Dec
Gate 1:
 reviews, merges, fresh-clone test, README.
Deadlines per person
All deadlines are
end of day (23:59 Cairo time)
 unless stated otherwise.
Zeyad (team lead)
By Tue 24 Nov: add everyone as collaborators, push the brief, this file and the design documents to
main
, then turn on branch
protection for
main
.
1.
Thu 26 Nov:
 open the PR with
omar_reference_scenario.md
 (nine labelled synthetic decisions, T01–T05 scores and confidences,
hand-computed T06 values). Roney is blocked until this is merged.
2.
Sat 28 Nov:
 open the PR with
docs/design/t06_policy.md
 (formula, tiers, shift-flag rule and how its window and threshold are
calibrated).
3.
Wed 2 Dec:
 open the PR with
self_consistency.py
 and
test_self_consistency.py
.
4.
Fri 4 Dec:
test_gate1_profile_engine.py
 passing; all PRs merged; fresh-clone run; README,
requirements.txt
 and
file_structure.txt
 updated; approval line of the Task 4 report filled. Also: review WP1 within a few hours of its PR (Thu 26 Nov),
because everything waits for it.
Habiba Ahmed Abdo — WP1 Models and Configuration
1.
Thu 26 Nov:
 PR opened with
common/models.py
,
common/config.py
, and
pydantic
 added to
requirements.txt
.
2.
Thu 26 Nov:
 same PR contains
test_models.py
,
test_config.py
 (the six valid fixtures round-trip; every invalid fixture is
rejected).
3.
Fri 27 Nov:
 any review comments fixed so the PR can be merged. After merging, she
peer-reviews Ahmed's storage PRs
 (design
on 27 Nov, code on 1 Dec). This is the most time-critical item in the task. If you cannot finish it by 26 Nov, say so on 25 Nov.
Ahmed Osama Ahmed — WP2 Storage
1.
Fri 27 Nov:
 PR opened with
wp2_storage_design.md
 (tables, columns, repository methods, how append-only and account deletion
work). Zeyad and Habiba review it on 27–28 Nov, before you code.
2.
Tue 1 Dec:
 PR opened with
storage/interfaces.py
 and
storage/sqlite_store.py
.

3.
Tue 1 Dec:
 same PR contains
test_storage_contract.py
, passing on an in-memory and a file database. Storage must be merged
by Wed 2 Dec because Esawy's isolation tests and the Gate 1 test depend on it.
Mohamed Abdelhakam Abdelaal — WP3 Aggregation
1.
Sat 28 Nov:
 PR opened with
docs/design/aggregation_policy.md
 (formulas, null handling, the confidence rule and its four
required properties).
2.
Sat 28 Nov:
 same PR contains
tests/fixtures/aggregation_oracle.json
 (at least 12 cases, hand-computed with the working
shown) and
wp3_open_points.md
.
3.
Wed 2 Dec:
 PR opened with
profiling/aggregation.py
 and
test_aggregation.py
 (every oracle case passes; functions are pure).
Also: peer-review Zeyad's T06 PRs (policy on 28 Nov, code on 2 Dec).
Mohamed Ali Alaily — WP5 Session state machine and human review
1.
Sat 28 Nov:
 human review of the Task 4 flagged items completed in
human_review/
 (verdict plus one-line reason for each item).
2.
Sun 29 Nov:
 comparison with Shams's independent verdicts done;
wp5_human_review_summary.md
 delivered (counts per verdict,
disagreements, patterns).
3.
Tue 1 Dec:
 PR opened with
sessions/state.py
 and
test_session_state.py
 (every transition, the exact 7-day reminder boundary,
late approval keeps the decision date). Also: peer-review Habiba's WP1 PR on 26–27 Nov (fast turnaround needed).
Shams Amr Saber Zaki — WP6 Quiz module
1.
Sat 28 Nov:
 PR opened with
scripts/build_quiz_content.py
, the client-safe
quiz_content_v1.json
, the server-side
quiz_key_v1.json
, the manifest, and
test_quiz_content.py
 (no gold fields anywhere in the served file).
2.
Sat 28 Nov:
 your
independent
 second pass of the Task 4 human review is finished and sent to Mohamed Ali. Do this
before
looking at his verdicts.
3.
Tue 1 Dec:
 PR opened with
quiz/content.py
,
quiz/scoring.py
 and
test_quiz_scoring.py
 (all 125 answer records map to their
gold values). Also: peer-review Mohamed Ali's state-machine PR (1–2 Dec).
Mohamed Esawy Elmeshad — WP7 Security and privacy
1.
Sat 28 Nov:
 PR opened with
security_baseline_stage_ab.md
 (threat table with controls, tests and OWASP references) and
privacy_notice_draft.md
.
2.
Sat 28 Nov:
 same PR contains
scripts/check_secrets.py
 and
test_security_baseline.py
.
3.
Thu 3 Dec:
 PR opened with
test_user_isolation.py
 and the static SQL-construction test, run against the merged storage layer.
Report any weakness to Ahmed and Zeyad in the PR; do not edit
storage/
. Also: peer-review Roney's synthetic-data PR (2–3
Dec).
Roney Maged Morkes — WP8 Synthetic data
1.
Wed 25 – Sat 28 Nov:
 environment set up, brief read, and
peer review of Esawy's security documents
 (Esawy's PR is due Sat 28
Nov; review within 24 hours, so by Sun 29 Nov). Read
omar_reference_scenario.md
 as soon as it is merged.
2.
Wed 2 Dec:
 PR opened with
common/synthetic.py
,
scripts/make_synthetic_users.py
, the generated
synthetic_users_v1.json
,
and
test_synthetic.py
 (deterministic with the same seed; all records flagged; the Omar user matches the scenario file exactly).
3.
Wed 2 Dec:
 the labelling guard
refuse_unlabelled
 is in the same PR, with its test. Start coding on Fri 27 Nov if WP1 and the Omar
file are merged; do not wait for 29 Nov.
Check-ins
Sat 28 Nov, 15 minutes, whole team:
 is WP1 merged? Is every Wave 1 document delivered? Who needs help for Wave 2? Anything
that will slip is announced here.
Thu 3 Dec, 10 minutes, whole team:
 list what is still unreviewed so Fri 4 Dec is only merging.
If you fall behind
1.
Tell the group the same day, with a new date you can really meet.
2.
Never push to
main
 to catch up, and never skip tests.
3.
If your item blocks someone else (WP1, Omar file, storage), Zeyad may reassign part of it to avoid delaying the whole team.
Definition of "done" for the whole task (Fri 4 Dec)
All eight work packages merged,
pytest -q
 green on a fresh clone with a fresh virtual environment, the Gate 1 integration test passing
(the Omar user goes through storage, aggregation and T06 and matches the hand-computed values), and no frozen Task 4 file changed.
