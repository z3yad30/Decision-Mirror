# WP3 Open Points

No rule is left unsettled in this lead-fix verification.

The confidence constant is fixed to `k = 1.0` in the policy, rather than
introducing a `confidence_k` setting that is absent from WP1 configuration.
The WP3 policy therefore uses only setting names already present in
`src/decision_mirror/common/config.py`: `quiz_weight`,
`situational_weight`, `quiz_confidence`, and
`recency_half_life_days`. No mismatches remain.
