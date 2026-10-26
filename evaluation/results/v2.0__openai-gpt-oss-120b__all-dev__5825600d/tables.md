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
| T01 | 14 | 93.3% | 0.100 | 50.0% | 100.0% | 0.829 | 0.950 | 100.0% | 0 |
| T02 | 15 | 100.0% | 0.069 | 66.7% | 100.0% | 0.889 | 0.957 | 100.0% | 0 |
| T03 | 15 | 100.0% | 0.043 | 86.7% | 100.0% | 0.967 | 0.972 | 100.0% | 0 |
| T04 | 14 | 93.3% | 0.107 | 50.0% | 100.0% | 0.851 | 0.838 | 100.0% | 0 |
| T05 | 15 | 100.0% | 0.049 | 80.0% | 100.0% | 0.952 | 0.944 | 100.0% | 0 |
| overall | 73 | 97.3% | 0.073 | 67.1% | 100.0% | 0.906 | 0.918 | 100.0% | 0 |

## Quiz confusion matrix (overall)

| Gold band / predicted band | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| 0 | 7 | 8 | 0 | 0 | 0 |
| 1 | 3 | 12 | 0 | 0 | 0 |
| 2 | 0 | 1 | 11 | 1 | 0 |
| 3 | 0 | 0 | 1 | 14 | 0 |
| 4 | 0 | 0 | 0 | 10 | 5 |

## Quiz 95% bootstrap confidence intervals

| Trait | MAE | Exact band accuracy | Spearman rho |
|---|---|---|---|
| T01 | [0.046, 0.146] (n=14) | [0.286, 0.786] (n=14) | [0.841, 0.993] (n=14) |
| T02 | [0.025, 0.119] (n=15) | [0.400, 0.867] (n=15) | [0.873, 0.992] (n=15) |
| T03 | [0.020, 0.077] (n=15) | [0.667, 1.000] (n=15) | [0.914, 0.996] (n=15) |
| T04 | [0.057, 0.157] (n=14) | [0.214, 0.786] (n=14) | [0.586, 0.921] (n=14) |
| T05 | [0.017, 0.087] (n=15) | [0.600, 1.000] (n=15) | [0.813, 0.992] (n=15) |
| overall | [0.053, 0.094] (n=73) | [0.562, 0.781] (n=73) | [0.873, 0.947] (n=73) |

## Organic metrics

| Metric | Value |
|---|---:|
| Paired numeric scores | 15 |
| MAE | 0.105 |
| Exact band accuracy | 46.7% |
| Missed-signal rate | 11.8% |
| Unsupported-inference rate | 15.4% |
| Status accuracy | 100.0% |
| Situational-factor precision | 60.0% |
| Situational-factor recall | 100.0% |
| Situational-factor category agreement | 0.0% |
| Confidence MAE (unambiguous gold) | 0.177 |
| Evidence token-overlap F1 (report only) | 0.261 |

## Evidence, edge cases, and readiness

| Metric | Value |
|---|---:|
| Evidence grounding | 97.6% |
| Edge-case checks | 39/47 (83.0%) |
| T06 violations | 0 |

Readiness thresholds are proposed and pending team lead approval.

| Criterion | Observed | Threshold | Result |
|---|---:|---:|---|
| strict_schema_valid_rate | 100.0% | at_least 95.0% | pass |
| schema_valid_or_recovered_rate | 100.0% | at_least 99.0% | pass |
| quiz_target_non_null_rate | 97.3% | at_least 90.0% | pass |
| quiz_exact_band_accuracy | 67.1% | at_least 60.0% | pass |
| quiz_within_one_band_rate | 100.0% | at_least 90.0% | pass |
| quiz_mae | 0.073 | at_most 0.15 | pass |
| quiz_direction_accuracy | 100.0% | at_least 90.0% | pass |
| quiz_spearman_rho | 0.918 | at_least 0.8 | pass |
| quiz_polarity_inversion_rate | 0.0% | at_most 2.0% | pass |
| evidence_grounding_rate | 97.6% | at_least 98.0% | fail |
| t06_violations | 0.000 | equal 0 | pass |
| edge_case_pass_rate | 83.0% | at_least 80.0% | pass |
| organic_situational_factor_recall | 100.0% | at_least 80.0% | pass |
