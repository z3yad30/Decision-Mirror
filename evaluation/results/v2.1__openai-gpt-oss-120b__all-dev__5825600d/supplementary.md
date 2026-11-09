# Post-hoc supplementary analyses — v2.1__openai-gpt-oss-120b__all-dev__5825600d

**post-hoc: added after dev and held-out results were seen.** These analyses are supplementary and do not alter `metrics.json`, `tables.md`, or report headline values.

## Quiz non-target traits

Each quiz gold record contains one target trait and one score; no non-target trait labels are supplied.
Off-target scoring is descriptive, not an error rate. Quiz non-target traits and T06 are unassessed against gold.

Off-target scoring: 36/300 (12.0%).

| Quiz item | Target trait | Non-target scored traits (score; confidence; evidence quotes; grounded) |
|---|---|---|
| Q02_A | T01 | T02=0.150; confidence=0.55; quotes=yes; grounded=yes; T03=0.700; confidence=0.6; quotes=yes; grounded=yes; T05=0.200; confidence=0.55; quotes=yes; grounded=yes |
| Q02_B | T01 | T05=0.150; confidence=0.6; quotes=yes; grounded=yes |
| Q02_C | T01 | none |
| Q02_D | T01 | T05=0.720; confidence=0.68; quotes=yes; grounded=yes |
| Q02_E | T01 | T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q03_A | T01 | none |
| Q03_B | T01 | T05=0.850; confidence=0.68; quotes=yes; grounded=yes |
| Q03_C | T01 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q03_D | T01 | T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q03_E | T01 | T05=0.150; confidence=0.55; quotes=yes; grounded=yes |
| Q04_A | T01 | none |
| Q04_B | T01 | T02=0.300; confidence=0.6; quotes=yes; grounded=yes |
| Q04_C | T01 | none |
| Q04_D | T01 | none |
| Q04_E | T01 | T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q06_A | T02 | none |
| Q06_B | T02 | none |
| Q06_C | T02 | none |
| Q06_D | T02 | none |
| Q06_E | T02 | T01=0.700; confidence=0.6; quotes=yes; grounded=yes; T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q09_A | T02 | none |
| Q09_B | T02 | T01=0.650; confidence=0.62; quotes=yes; grounded=yes; T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q09_C | T02 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q09_D | T02 | none |
| Q09_E | T02 | none |
| Q10_A | T02 | none |
| Q10_B | T02 | none |
| Q10_C | T02 | T05=0.500; confidence=0.6; quotes=yes; grounded=yes |
| Q10_D | T02 | none |
| Q10_E | T02 | none |
| Q11_A | T03 | none |
| Q11_B | T03 | none |
| Q11_C | T03 | none |
| Q11_D | T03 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q11_E | T03 | none |
| Q13_A | T03 | none |
| Q13_B | T03 | none |
| Q13_C | T03 | none |
| Q13_D | T03 | none |
| Q13_E | T03 | none |
| Q14_A | T03 | none |
| Q14_B | T03 | none |
| Q14_C | T03 | none |
| Q14_D | T03 | T02=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q14_E | T03 | T01=0.650; confidence=0.6; quotes=yes; grounded=yes; T02=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q17_A | T04 | T05=0.700; confidence=0.65; quotes=yes; grounded=yes |
| Q17_B | T04 | T05=0.700; confidence=0.82; quotes=yes; grounded=yes |
| Q17_C | T04 | none |
| Q17_D | T04 | T05=0.300; confidence=0.75; quotes=yes; grounded=yes |
| Q17_E | T04 | T05=0.150; confidence=0.6; quotes=yes; grounded=yes |
| Q18_A | T04 | T05=0.700; confidence=0.68; quotes=yes; grounded=yes |
| Q18_B | T04 | none |
| Q18_C | T04 | T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q18_D | T04 | none |
| Q18_E | T04 | T05=0.300; confidence=0.6; quotes=yes; grounded=yes |
| Q19_A | T04 | T05=0.700; confidence=0.65; quotes=yes; grounded=yes |
| Q19_B | T04 | T05=0.700; confidence=0.85; quotes=yes; grounded=yes |
| Q19_C | T04 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q19_D | T04 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q19_E | T04 | T05=0.300; confidence=0.6; quotes=yes; grounded=yes |
| Q21_A | T05 | none |
| Q21_B | T05 | none |
| Q21_C | T05 | none |
| Q21_D | T05 | none |
| Q21_E | T05 | none |
| Q22_A | T05 | T01=0.700; confidence=0.65; quotes=yes; grounded=yes |
| Q22_B | T05 | none |
| Q22_C | T05 | T04=0.300; confidence=0.55; quotes=yes; grounded=yes |
| Q22_D | T05 | none |
| Q22_E | T05 | none |
| Q23_A | T05 | none |
| Q23_B | T05 | none |
| Q23_C | T05 | none |
| Q23_D | T05 | none |
| Q23_E | T05 | none |

Off-target cases for human review (no decisions made):
- `Q02_A`: T02, T03, T05
- `Q02_B`: T05
- `Q02_D`: T05
- `Q02_E`: T05
- `Q03_B`: T05
- `Q03_C`: T05
- `Q03_D`: T05
- `Q03_E`: T05
- `Q04_B`: T02
- `Q04_E`: T05
- `Q06_E`: T01, T05
- `Q09_B`: T01, T05
- `Q09_C`: T05
- `Q10_C`: T05
- `Q11_D`: T05
- `Q14_D`: T02
- `Q14_E`: T01, T02
- `Q17_A`: T05
- `Q17_B`: T05
- `Q17_D`: T05
- `Q17_E`: T05
- `Q18_A`: T05
- `Q18_C`: T05
- `Q18_E`: T05
- `Q19_A`: T05
- `Q19_B`: T05
- `Q19_C`: T05
- `Q19_D`: T05
- `Q19_E`: T05
- `Q22_A`: T01
- `Q22_C`: T04

## Situational factors

Precision, recall, and category agreement are each already reported separately in the existing `metrics.json`; values below preserve those numbers and expose denominators.

- Precision: 2/4 = 50.0% (TP/TP+FP).
- Recall: 2/3 = 66.7% (TP/TP+FN).
- Category agreement: 0/2 = 0.0% among true positives.

**Small-n warning:** Organic split sizes and positive-factor counts are small; these rates are descriptive and should not be treated as stable estimates.

## Quote-normalizer comparison

Original normalizer recovered from Git (`523adc3:evaluation/metrics.py`), SHA-256 `13c87f186970111d09641cb0ee3aa2678722300d6a44eeac350472c301fa7e6c`; corrected official normalizer SHA-256 `45ce8a0186c85b7949ecb0579c41b42c3c55ae005aa5268cb145190682df8ef4`.
Grounded quotes: original 159/159 (100.0%); corrected 159/159 (100.0%).

| Item | Trait | Quote | Original | Corrected |
|---|---|---|---|---|
| None | — | No quote status changed. | — | — |

## Quiz question-level cluster bootstrap

Resampling unit: one quiz question with its five answer options. 2000 replicates; seed 42; 15 overall question clusters.
**Stability limitation:** 15 question clusters overall (and only 3 clusters for an individual trait) is too small to support stable intervals.

| Trait | Clusters | MAE item point [CI] | MAE cluster point [CI] | Exact-band item point [CI] | Exact-band cluster point [CI] | Spearman item point [CI] | Spearman cluster point [CI] | Direction item point (no CI stored) | Direction cluster point [CI] |
|---|---:|---|---|---|---|---:|---|---:|---|
| T01 | 3 | 0.094 [0.045, 0.143] | 0.094 [0.088, 0.105] | 0.571 [0.286, 0.857] | 0.571 [0.500, 0.600] | 0.922 [0.754, 0.993] | 0.922 [0.738, 0.975] | 100.0% | 1.000 [1.000, 1.000] |
| T02 | 3 | 0.053 [0.013, 0.100] | 0.053 [0.040, 0.070] | 0.733 [0.467, 0.933] | 0.733 [0.600, 0.800] | 0.963 [0.891, 0.997] | 0.963 [0.963, 0.975] | 100.0% | 1.000 [1.000, 1.000] |
| T03 | 3 | 0.043 [0.013, 0.080] | 0.043 [0.020, 0.060] | 0.867 [0.667, 1.000] | 0.867 [0.800, 1.000] | 0.956 [0.800, 0.999] | 0.956 [0.950, 1.000] | 100.0% | 1.000 [1.000, 1.000] |
| T04 | 3 | 0.104 [0.038, 0.183] | 0.104 [0.067, 0.120] | 0.583 [0.333, 0.833] | 0.583 [0.400, 0.750] | 0.777 [0.330, 0.950] | 0.777 [0.400, 0.866] | 100.0% | 1.000 [1.000, 1.000] |
| T05 | 3 | 0.033 [0.007, 0.067] | 0.033 [0.010, 0.070] | 0.867 [0.667, 1.000] | 0.867 [0.600, 1.000] | 0.982 [0.921, 1.000] | 0.982 [0.975, 1.000] | 100.0% | 1.000 [1.000, 1.000] |
| overall | 15 | 0.064 [0.043, 0.085] | 0.064 [0.047, 0.081] | 0.732 [0.620, 0.831] | 0.732 [0.636, 0.824] | 0.916 [0.855, 0.954] | 0.916 [0.865, 0.953] | 100.0% | 1.000 [1.000, 1.000] |

Direction has no stored item-level confidence interval; only its existing point estimate is shown. Threshold comparisons below are information only; no pre-registered threshold was changed.

| Metric | Preregistered threshold | Cluster lower bound | Lower bound alone meets threshold | Relevant bound meets threshold |
|---|---|---:|---|---|
| mae | at_most 0.150 | 0.047 | True | True (upper bound) |
| exact_band_accuracy | at_least 0.600 | 0.636 | True | True (lower bound) |
| spearman_rho | at_least 0.800 | 0.865 | True | True (lower bound) |
| direction_accuracy | at_least 0.900 | 1.000 | True | True (lower bound) |

For quiz gold, the evaluated trait set is the target trait only. Organic T01–T05, including gold-null unsupported-inference opportunities, and edge-case behavior are evaluated against their respective reference sets in the existing metrics. Quiz non-target traits and T06 are unassessed against gold.
