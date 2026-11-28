# Aggregation Policy: current trait scores from the observation history

**Status: PROPOSED** (pending approval by Zeyad) · Owner: Mohamed Abdelhakam Abdelaal (WP3, Data Science) · Task 5, Wave 1
Code that implements this: `src/decision_mirror/profiling/aggregation.py` (Wave 2, not part of this document).
Hand-computed checks: `tests/fixtures/aggregation_oracle.json`. Unsettled points: `docs/tasks/task-5-profile-engine/notes/wp3_open_points.md`.

## 1. Purpose and constraints from Task 4

The history of observations is the source of truth (Chapter 3 §3.3). The current score and confidence of each trait are *computed* from it and can be recomputed if this policy changes. The Task 4 handoff (`07_handoff_to_profile_aggregation.md`) sets these constraints, and this policy follows them:

- A null score is "no evidence", never a midpoint. It is not replaced by 0.5.
- `confidence` is an evidence-quality weight, not a calibrated probability. It is used here only as a *relative weight*, with no assumed transform.
- A situational factor lowers the weight of that observation. It is not turned into a user attribute and is not evidence for a trait.
- The factor's **category is not used**, because category agreement was weak in Task 4.

## 2. Input and output

**Input:** the observations of **one user** for **one trait** (T01–T05), plus `Settings`. An observation has `trait_id`, `score` (0–1 or null), `confidence` (0–1), `source` (`quiz` | `decision`) and `situational_factor` (null or object). The engine receives only stored observations. Only approved decisions and the quiz have observations (WP2 rule), so the engine does no status filtering. The order of the list does not matter.

**Output `TraitState`:** `score` (float or null), `confidence` (float 0–1), `status` (`sufficient` | `insufficient`), `n_observations_used`, `n_quiz`, `n_decision`.

`compute_profile` runs `compute_trait_state` for T01–T05 only. **T06 observations are ignored** (T06 is computed in WP4 from decisions) and the key `T06` is not in the result.

## 3. Formulas

For observation *i* of the trait with score `s_i`, confidence `c_i`:

```
source_weight_i       = quiz_weight   if source_i == quiz,  else 1
situational_weight_i  = situational_weight   if situational_factor_i is not null,  else 1
w_i = c_i × source_weight_i × situational_weight_i          (recency_i = 1 in v1, see §6)
```

Null-score observations are **dropped before anything else**. Observations with `w_i = 0` are also dropped from the counts (they cannot change the result).

```
W      = Σ w_i                    over the kept observations
score  = ( Σ w_i × s_i ) / W      (weighted mean, always inside [0, 1])
confidence = W / (W + k)          k = 1.0
status = sufficient
```

**No usable evidence** (no kept observation, i.e. empty history, all nulls, or `W = 0`):
`score = null`, `confidence = 0.0`, `status = insufficient`, all counts 0. The engine never returns a number for such a trait.

`n_observations_used` = number of kept observations; `n_quiz` / `n_decision` split that count by source.

No rounding is done inside the engine. Tests compare with tolerance 1e-9.

## 4. Settings used (all in `config.Settings`, none hard-coded)

| Setting | PROPOSED default | Role here |
|---|---|---|
| `quiz_weight` | 0.5 | source weight of a quiz observation |
| `situational_weight` | 0.5 | multiplier when `situational_factor` is not null (any category) |
| `recency_half_life_days` | None | unused in v1 (see §6) |

`quiz_confidence` (0.30) is applied when the quiz module creates the observation (WP6). The engine just reads the `confidence` stored on each observation.

## 5. Confidence rule and why

`confidence = W / (W + k)` where `W` is the total evidence weight and the
constant `k` is fixed at `1.0` in version 1.

- It grows smoothly with the amount of evidence, rises quickly at first and then flattens, and never reaches 1. This avoids claiming certainty from a few observations.
- `k` is the amount of weight at which confidence is exactly 0.5. With `k = 1.0`, confidence is 0.5 at one unit of weighted evidence.
- It depends only on how much weighted evidence exists, not on whether observations agree. Consistency over time is the job of T06. Two opposite decisions therefore give a middling score at normal confidence (case `conflicting_scores`). This is intentional and is open point 3.

Reference values (defaults, k = 1.0):

| Situation | W | confidence |
|---|---|---|
| quiz only, 5 observations (0.3 × 0.5 each) | 0.75 | 0.429 |
| 1 decision, c = 0.7 | 0.7 | 0.412 |
| 3 decisions, c = 0.6 / 0.6 / 0.6 | 1.8 | 0.643 |
| 10 decisions, c = 0.7 | 7.0 | 0.875 |

### Required properties (each is a test)

| | Property | Why it holds | Oracle case / property test |
|---|---|---|---|
| (a) | No data gives 0.0 | By the "no usable evidence" rule | `empty_history`, `all_nulls`, `zero_weight_only` |
| (b) | Quiz-only has lower confidence than 3+ decisions of moderate confidence | `W/(W+k)` is strictly increasing in `W`. A trait has at most 5 quiz observations, so quiz-only `W ≤ 5 × 0.3 × 0.5 = 0.75`. Three non-situational decisions with `c ≥ 0.6` give `W ≥ 1.8`. | `quiz_only_five` (0.429) < `three_decisions` (0.677); property test over a grid of confidences 0.5–1.0 and 3–10 decisions |
| (c) | Adding a consistent observation never lowers confidence | Every weight is ≥ 0, so `W` cannot fall, and the function is increasing in `W`. This holds for any added scored observation, and the property test uses consistent ones as required. | property test: add observations one by one and assert confidence is non-decreasing |
| (d) | Confidence is always in [0, 1] | `W ≥ 0`, `k > 0` give `0 ≤ W/(W+k) < 1` | property test over random histories, plus every oracle case |

Property (b) depends on the defaults. It is guaranteed when `n_quiz_per_trait × quiz_confidence × quiz_weight < 3 × 0.5`. The default is 0.75 < 1.5. A configuration that breaks this inequality should be rejected or at least flagged (open point 4).

## 6. Where recency would plug in (not used in v1)

`recency_half_life_days = None` means no decay. If it is set later, one extra factor is added to the weight, with age measured to an `as_of` date **passed into** the function (the engine never reads the clock):

```
recency_i = 0.5 ^ ( age_days_i / recency_half_life_days ),    age_days_i = as_of − decision_date_i
w_i = c_i × source_weight_i × situational_weight_i × recency_i
```

This needs `decision_date` on each observation (not in the current observation shape, so a later change to the input of the engine is needed). The decision date, not the approval date, must be used. Quiz observations would need a defined date (the sign-up date). Nothing else in this policy changes.

## 7. Quiz and decisions disagree

No special rule. The weighted mean already handles it: the quiz carries `quiz_weight × quiz_confidence = 0.15` per observation, a decision carries up to 1.0, so decisions outweigh the quiz as they accumulate (case `quiz_plus_decisions`). The quiz is never deleted or overridden. It stays in the history and in the counts (`n_quiz`).

## 8. Purity

The functions never modify their input list or its objects, never read the clock, and never touch storage or the network. The same input and settings always give the same output (test with a deep copy and two runs).

## 9. What this policy does not do

- It does not look at the situational factor's category or description.
- It does not filter by session status, date or user. The caller passes one user's observations.
- It does not compute T06, shift flags or tiers (WP4).
- It does not claim calibrated probabilities. `confidence` is a relative evidence-weight score.
- It has not been validated on real users. It is validated only against the hand-computed oracle. Weights and `k` are proposals for Zeyad to approve (Open decision 1 in the brief).
