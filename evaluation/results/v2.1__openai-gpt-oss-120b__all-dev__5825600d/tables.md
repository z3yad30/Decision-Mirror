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
| T01 | 14 | 93.3% | 0.094 | 57.1% | 100.0% | 0.857 | 0.922 | 100.0% | 0 |
| T02 | 15 | 100.0% | 0.053 | 73.3% | 100.0% | 0.917 | 0.963 | 100.0% | 0 |
| T03 | 15 | 100.0% | 0.043 | 86.7% | 100.0% | 0.967 | 0.956 | 100.0% | 0 |
| T04 | 12 | 80.0% | 0.104 | 58.3% | 91.7% | 0.800 | 0.777 | 100.0% | 0 |
| T05 | 15 | 100.0% | 0.033 | 86.7% | 100.0% | 0.967 | 0.982 | 100.0% | 0 |
| overall | 71 | 94.7% | 0.064 | 73.2% | 98.6% | 0.912 | 0.916 | 100.0% | 0 |

## Quiz confusion matrix (overall)

| Gold band / predicted band | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| 0 | 6 | 8 | 0 | 0 | 0 |
| 1 | 2 | 13 | 0 | 0 | 0 |
| 2 | 0 | 1 | 11 | 0 | 1 |
| 3 | 0 | 0 | 0 | 15 | 0 |
| 4 | 0 | 0 | 0 | 7 | 7 |

## Quiz 95% bootstrap confidence intervals

| Trait | MAE | Exact band accuracy | Spearman rho |
|---|---|---|---|
| T01 | [0.045, 0.143] (n=14) | [0.286, 0.857] (n=14) | [0.754, 0.993] (n=14) |
| T02 | [0.013, 0.100] (n=15) | [0.467, 0.933] (n=15) | [0.891, 0.997] (n=15) |
| T03 | [0.013, 0.080] (n=15) | [0.667, 1.000] (n=15) | [0.800, 0.999] (n=15) |
| T04 | [0.038, 0.183] (n=12) | [0.333, 0.833] (n=12) | [0.330, 0.950] (n=12) |
| T05 | [0.007, 0.067] (n=15) | [0.667, 1.000] (n=15) | [0.921, 1.000] (n=15) |
| overall | [0.043, 0.085] (n=71) | [0.620, 0.831] (n=71) | [0.855, 0.954] (n=71) |

## Organic metrics

| Metric | Value |
|---|---:|
| Paired numeric scores | 13 |
| MAE | 0.104 |
| Exact band accuracy | 46.2% |
| Missed-signal rate | 23.5% |
| Unsupported-inference rate | 8.3% |
| Status accuracy | 100.0% |
| Situational-factor precision | 50.0% |
| Situational-factor recall | 66.7% |
| Situational-factor category agreement | 0.0% |
| Confidence MAE (unambiguous gold) | 0.146 |
| Evidence token-overlap F1 (report only) | 0.281 |

## Evidence, edge cases, and readiness

| Metric | Value |
|---|---:|
| Evidence grounding | 100.0% |
| Edge-case checks | 40/47 (85.1%) |
| T06 violations | 0 |

Readiness thresholds are proposed and pending team lead approval.

| Criterion | Observed | Threshold | Result |
|---|---:|---:|---|
| strict_schema_valid_rate | 100.0% | at_least 95.0% | pass |
| schema_valid_or_recovered_rate | 100.0% | at_least 99.0% | pass |
| quiz_target_non_null_rate | 94.7% | at_least 90.0% | pass |
| quiz_exact_band_accuracy | 73.2% | at_least 60.0% | pass |
| quiz_within_one_band_rate | 98.6% | at_least 90.0% | pass |
| quiz_mae | 0.064 | at_most 0.15 | pass |
| quiz_direction_accuracy | 100.0% | at_least 90.0% | pass |
| quiz_spearman_rho | 0.916 | at_least 0.8 | pass |
| quiz_polarity_inversion_rate | 0.0% | at_most 2.0% | pass |
| evidence_grounding_rate | 100.0% | at_least 98.0% | pass |
| t06_violations | 0.000 | equal 0 | pass |
| edge_case_pass_rate | 85.1% | at_least 80.0% | pass |
| organic_situational_factor_recall | 66.7% | at_least 80.0% | fail |
