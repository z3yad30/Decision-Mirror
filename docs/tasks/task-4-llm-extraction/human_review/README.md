# Task 4 evidence cross-review

`cross_review.csv` contains the `needs_manual_review` cases recorded in the
v2.0 development and held-out `error_log.jsonl` files. It contains no review
decisions; every row is `PENDING`.

For each row, independently assess whether the quoted evidence supports the
extracted score for the listed trait. Use only one of these decisions:

- `supports`
- `partially_supports`
- `does_not_support`
- `unclear`

Enter the decision and any explanation in `reviewer_decision` and
`reviewer_comments`, then update `review_status` only after review. Do not infer
a decision from the numeric match or from the automated flag. The exact
reviewer question is included in every row.

Rows are deterministically shuffled with Python `random.Random(42)` after
sorting by run, item, and trait. A flagged item may produce one row per
exact-band-matching trait. Review all rows; do not treat this CSV as a set of
automated error findings.
