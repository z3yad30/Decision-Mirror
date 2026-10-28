# Evaluation tables

## Format compliance

| Metric | Value |
|---|---:|
| strict_json_parse_rate | 100.0% |
| schema_valid_rate | 100.0% |
| semantic_valid_rate | 100.0% |
| recovered_rate | 0.0% |

## Quiz target-trait scoring

| Trait | N | Non-null | MAE | Exact band | Within one | QWK | Spearman | Direction | Inversions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| T01 | 9 | 90.0% | 0.063 | 66.7% | 100.0% | 0.867 | 0.979 | 100.0% | 0 |
| T02 | 9 | 90.0% | 0.063 | 66.7% | 100.0% | 0.903 | 0.960 | 100.0% | 0 |
| T03 | 9 | 90.0% | 0.052 | 77.8% | 100.0% | 0.950 | 0.902 | 100.0% | 0 |
| T04 | 9 | 90.0% | 0.128 | 33.3% | 100.0% | 0.784 | 0.853 | 100.0% | 0 |
| T05 | 10 | 100.0% | 0.042 | 80.0% | 100.0% | 0.941 | 0.975 | 100.0% | 0 |
| overall | 46 | 92.0% | 0.069 | 65.2% | 100.0% | 0.898 | 0.927 | 100.0% | 0 |

## Quiz confusion matrix (overall)

| Gold band / predicted band | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| 0 | 4 | 5 | 0 | 0 | 0 |
| 1 | 1 | 8 | 0 | 0 | 0 |
| 2 | 0 | 1 | 6 | 1 | 0 |
| 3 | 0 | 0 | 0 | 10 | 0 |
| 4 | 0 | 0 | 0 | 8 | 2 |

## Quiz 95% bootstrap confidence intervals

| Trait | MAE | Exact band accuracy | Spearman rho |
|---|---|---|---|
| T01 | [0.011, 0.118] (n=9) | [0.333, 1.000] (n=9) | [0.872, 1.000] (n=9) |
| T02 | [0.007, 0.122] (n=9) | [0.333, 1.000] (n=9) | [0.777, 1.000] (n=9) |
| T03 | [0.004, 0.113] (n=9) | [0.444, 1.000] (n=9) | [0.534, 1.000] (n=9) |
| T04 | [0.061, 0.178] (n=9) | [0.111, 0.667] (n=9) | [0.579, 0.962] (n=9) |
| T05 | [0.005, 0.086] (n=10) | [0.500, 1.000] (n=10) | [0.877, 1.000] (n=10) |
| overall | [0.044, 0.094] (n=46) | [0.522, 0.783] (n=46) | [0.861, 0.964] (n=46) |

## Organic metrics

| Metric | Value |
|---|---:|
| Paired numeric scores | 7 |
| MAE | 0.079 |
| Exact band accuracy | 57.1% |
| Missed-signal rate | 0.0% |
| Unsupported-inference rate | 7.1% |
| Status accuracy | 100.0% |
| Situational-factor precision | 50.0% |
| Situational-factor recall | 100.0% |
| Situational-factor category agreement | 100.0% |
| Confidence MAE (unambiguous gold) | 0.077 |
| Evidence token-overlap F1 (report only) | 0.227 |

## Evidence, edge cases, and readiness

| Metric | Value |
|---|---:|
| Evidence grounding | 100.0% |
| Edge-case checks | 0/0 (n/a) |
| T06 violations | 0 |

Readiness thresholds are proposed and pending team lead approval.

| Criterion | Observed | Threshold | Result |
|---|---:|---:|---|
| strict_schema_valid_rate | 100.0% | at_least 95.0% | pass |
| schema_valid_or_recovered_rate | 100.0% | at_least 99.0% | pass |
| quiz_target_non_null_rate | 92.0% | at_least 90.0% | pass |
| quiz_exact_band_accuracy | 65.2% | at_least 60.0% | pass |
| quiz_within_one_band_rate | 100.0% | at_least 90.0% | pass |
| quiz_mae | 0.069 | at_most 0.15 | pass |
| quiz_direction_accuracy | 100.0% | at_least 90.0% | pass |
| quiz_spearman_rho | 0.927 | at_least 0.8 | pass |
| quiz_polarity_inversion_rate | 0.0% | at_most 2.0% | pass |
| evidence_grounding_rate | 100.0% | at_least 98.0% | pass |
| t06_violations | 0.000 | equal 0 | pass |
| edge_case_pass_rate | n/a | at_least 80.0% | not_applicable |
| organic_situational_factor_recall | 100.0% | at_least 80.0% | pass |
