# T06 Policy

**Status: PROPOSED**

Authored by: coding agent (lead run) — 2026-11-28

T06 (Self-Consistency) is a history-derived profile value for traits T01 through
T05. For each trait, include only decisions that are approved, have a non-null
score for that trait, and have no situational factor. Pending and rejected
decisions are excluded. A null score is excluded only for that trait; that
decision may remain usable for another trait. T06 is never extracted by the
LLM and is never inferred from a single narrative or quiz response.

For the usable population of `n` scores:

```text
mean = sum(scores) / n
population variance = sum((score - mean)^2) / n
population standard deviation = sqrt(population variance)
value = 1 - 2 * population standard deviation
```

Population standard deviation is used because the usable approved decisions are
the complete population for the current history, not an estimate of a larger
unobserved population. The sample standard deviation alternative is an open
point and would divide its squared deviations by `n - 1`; it is not used until
the team explicitly adopts it.

For the settings named in `src/decision_mirror/common/config.py`:

- fewer than `t06_min_usable` (4) usable decisions: `tier = hidden`
- at least 4 and fewer than `t06_strong_at` (8): `tier = moderate`
- at least 8: `tier = strong`

Thus the two thresholds give hidden for 0–3, moderate for 4–7, and strong for
8 or more usable decisions.

## Shift flag

A shift flag fires only when enough usable decisions exist to split the history
into two complete windows. The last `shift_window` usable decisions form the
recent mean; the `shift_window` decisions immediately before them form the earlier
mean. The absolute difference must be at least `shift_threshold`:

```text
shift_flag =
  too few decisions to split
    ? false
    : abs(mean(last shift_window) - mean(earlier shift_window))
      >= shift_threshold
```

If the usable history has fewer than `2 * shift_window` decisions, there are too
few decisions to form both windows and the shift flag is false. The same rule
applies after per-trait status, null, and situational exclusions.

Comparisons use decimal policy arithmetic. `shift_threshold` is converted to
`Decimal` rather than comparing binary floating-point means, so an exact
mathematical equality such as `0.10` is inclusive and fires (`>=`). No
tolerance is applied; values below the threshold remain false.

## Synthetic calibration

Authored by: coding agent (lead run) — 2026-11-28

The calibration uses six at-least-synthetic histories. The situational history
contains a decision with `situational_factor` set; that decision is removed
before shift means are evaluated.

| History | Synthetic usable sequence | Intent |
|---|---|---|
| Stable | `[0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50]` | No shift |
| Noisy but stable | `[0.45, 0.55, 0.47, 0.53, 0.46, 0.54, 0.48, 0.52]` | Noise is not drift |
| Gradual drift | `[0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55]` | Gradual shift |
| Abrupt shift | `[0.30, 0.30, 0.30, 0.30, 0.70, 0.70, 0.70, 0.70]` | Abrupt shift |
| Too short to split | `[0.20, 0.80]` | Insufficient history |
| One situational decision | `[0.20, 0.25, 0.30, 0.80(situational), 0.35, 0.40, 0.45, 0.50]` | Exclude situational observation |

The paired evaluation uses every `shift_window` in `{2, 3, 4}` and every
`shift_threshold` in `{0.10, 0.15, 0.20, 0.25}`. A table entry is `Y` when the
split mean difference meets the threshold and `N` otherwise.

| Window | Threshold | Stable | Noisy stable | Gradual drift | Abrupt shift | Too short | Situational excluded |
|---:|---:|---|---|---|---|---|---|
| 2 | 0.10 | N | N | Y | Y | N | Y |
| 2 | 0.15 | N | N | N | Y | N | N |
| 2 | 0.20 | N | N | N | N | N | N |
| 2 | 0.25 | N | N | N | N | N | N |
| 3 | 0.10 | N | N | Y | Y | N | Y |
| 3 | 0.15 | N | N | Y | Y | N | Y |
| 3 | 0.20 | N | N | N | Y | N | N |
| 3 | 0.25 | N | N | N | Y | N | N |
| 4 | 0.10 | N | N | Y | Y | N | N |
| 4 | 0.15 | N | N | Y | Y | N | N |
| 4 | 0.20 | N | N | Y | Y | N | N |
| 4 | 0.25 | N | N | N | Y | N | N |

The selected defaults are `shift_window = 4` and `shift_threshold = 0.15`.
This pair flags both gradual drift and abrupt shift while not flagging stable,
noisy-stable, too-short, or situational histories. It differs from the earlier
window placeholder of 3, so the window default is updated in configuration and
configuration tests.

## Aggregation boundary

T06 is not part of the aggregation engine in `profiling/aggregation.py`.
Aggregation handles T01–T05 observations; T06 remains a separate
history-derived computation in the later WP4 T06 implementation.