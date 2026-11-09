# Post-hoc supplementary analyses — v2.0__openai-gpt-oss-120b__all-heldout__5825600d

**post-hoc: added after dev and held-out results were seen.** These analyses are supplementary and do not alter `metrics.json`, `tables.md`, or report headline values.

## Quiz non-target traits

Each quiz gold record contains one target trait and one score; no non-target trait labels are supplied.
Off-target scoring is descriptive, not an error rate. Quiz non-target traits and T06 are unassessed against gold.

Off-target scoring: 31/200 (15.5%).

| Quiz item | Target trait | Non-target scored traits (score; confidence; evidence quotes; grounded) |
|---|---|---|
| Q01_A | T01 | none |
| Q01_B | T01 | T02=0.250; confidence=0.8; quotes=yes; grounded=yes; T05=0.850; confidence=0.9; quotes=yes; grounded=yes |
| Q01_C | T01 | T05=0.700; confidence=0.8; quotes=yes; grounded=yes |
| Q01_D | T01 | T02=0.650; confidence=0.8; quotes=yes; grounded=yes |
| Q01_E | T01 | T02=0.650; confidence=0.62; quotes=yes; grounded=yes; T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q05_A | T01 | T02=0.150; confidence=0.55; quotes=yes; grounded=yes; T05=0.700; confidence=0.63; quotes=yes; grounded=yes |
| Q05_B | T01 | none |
| Q05_C | T01 | none |
| Q05_D | T01 | none |
| Q05_E | T01 | T05=0.320; confidence=0.62; quotes=yes; grounded=yes |
| Q07_A | T02 | none |
| Q07_B | T02 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q07_C | T02 | T05=0.850; confidence=0.6; quotes=yes; grounded=yes |
| Q07_D | T02 | T05=0.650; confidence=0.65; quotes=yes; grounded=yes |
| Q07_E | T02 | none |
| Q08_A | T02 | none |
| Q08_B | T02 | none |
| Q08_C | T02 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q08_D | T02 | T05=0.650; confidence=0.62; quotes=yes; grounded=yes |
| Q08_E | T02 | T05=0.500; confidence=0.62; quotes=yes; grounded=yes |
| Q12_A | T03 | none |
| Q12_B | T03 | none |
| Q12_C | T03 | T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q12_D | T03 | none |
| Q12_E | T03 | none |
| Q15_A | T03 | none |
| Q15_B | T03 | none |
| Q15_C | T03 | none |
| Q15_D | T03 | none |
| Q15_E | T03 | none |
| Q16_A | T04 | T02=0.700; confidence=0.6; quotes=yes; grounded=yes; T05=0.700; confidence=0.6; quotes=yes; grounded=yes |
| Q16_B | T04 | T05=0.700; confidence=0.73; quotes=yes; grounded=yes |
| Q16_C | T04 | T02=0.700; confidence=0.65; quotes=yes; grounded=yes; T05=0.850; confidence=0.85; quotes=yes; grounded=yes |
| Q16_D | T04 | T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q16_E | T04 | T05=0.300; confidence=0.6; quotes=yes; grounded=yes |
| Q20_A | T04 | T05=0.750; confidence=0.6; quotes=yes; grounded=yes |
| Q20_B | T04 | T05=0.700; confidence=0.65; quotes=yes; grounded=yes |
| Q20_C | T04 | T05=0.650; confidence=0.6; quotes=yes; grounded=yes |
| Q20_D | T04 | none |
| Q20_E | T04 | T02=0.300; confidence=0.55; quotes=yes; grounded=yes; T05=0.200; confidence=0.55; quotes=yes; grounded=yes |
| Q24_A | T05 | none |
| Q24_B | T05 | none |
| Q24_C | T05 | none |
| Q24_D | T05 | none |
| Q24_E | T05 | none |
| Q25_A | T05 | T01=0.680; confidence=0.6; quotes=yes; grounded=yes; T02=0.350; confidence=0.55; quotes=yes; grounded=yes; T03=0.720; confidence=0.6; quotes=yes; grounded=yes |
| Q25_B | T05 | none |
| Q25_C | T05 | none |
| Q25_D | T05 | none |
| Q25_E | T05 | none |

Off-target cases for human review (no decisions made):
- `Q01_B`: T02, T05
- `Q01_C`: T05
- `Q01_D`: T02
- `Q01_E`: T02, T05
- `Q05_A`: T02, T05
- `Q05_E`: T05
- `Q07_B`: T05
- `Q07_C`: T05
- `Q07_D`: T05
- `Q08_C`: T05
- `Q08_D`: T05
- `Q08_E`: T05
- `Q12_C`: T05
- `Q16_A`: T02, T05
- `Q16_B`: T05
- `Q16_C`: T02, T05
- `Q16_D`: T05
- `Q16_E`: T05
- `Q20_A`: T05
- `Q20_B`: T05
- `Q20_C`: T05
- `Q20_E`: T02, T05
- `Q25_A`: T01, T02, T03

## Situational factors

Precision, recall, and category agreement are each already reported separately in the existing `metrics.json`; values below preserve those numbers and expose denominators.

- Precision: 1/2 = 50.0% (TP/TP+FP).
- Recall: 1/1 = 100.0% (TP/TP+FN).
- Category agreement: 1/1 = 100.0% among true positives.

**Small-n warning:** Organic split sizes and positive-factor counts are small; these rates are descriptive and should not be treated as stable estimates.

## Quote-normalizer comparison

Original normalizer recovered from Git (`523adc3:evaluation/metrics.py`), SHA-256 `13c87f186970111d09641cb0ee3aa2678722300d6a44eeac350472c301fa7e6c`; corrected official normalizer SHA-256 `45ce8a0186c85b7949ecb0579c41b42c3c55ae005aa5268cb145190682df8ef4`.
Grounded quotes: original 93/93 (100.0%); corrected 93/93 (100.0%).

| Item | Trait | Quote | Original | Corrected |
|---|---|---|---|---|
| None | — | No quote status changed. | — | — |

## Quiz question-level cluster bootstrap

Resampling unit: one quiz question with its five answer options. 2000 replicates; seed 42; 10 overall question clusters.
**Stability limitation:** 10 question clusters overall (and only 2 clusters for an individual trait) is too small to support stable intervals.

| Trait | Clusters | MAE item point [CI] | MAE cluster point [CI] | Exact-band item point [CI] | Exact-band cluster point [CI] | Spearman item point [CI] | Spearman cluster point [CI] | Direction item point (no CI stored) | Direction cluster point [CI] |
|---|---:|---|---|---|---|---:|---|---:|---|
| T01 | 2 | 0.063 [0.011, 0.118] | 0.063 [0.050, 0.074] | 0.667 [0.333, 1.000] | 0.667 [0.600, 0.750] | 0.979 [0.872, 1.000] | 0.979 [0.949, 1.000] | 100.0% | 1.000 [1.000, 1.000] |
| T02 | 2 | 0.063 [0.007, 0.122] | 0.063 [0.044, 0.088] | 0.667 [0.333, 1.000] | 0.667 [0.500, 0.800] | 0.960 [0.777, 1.000] | 0.960 [0.949, 0.975] | 100.0% | 1.000 [1.000, 1.000] |
| T03 | 2 | 0.052 [0.004, 0.113] | 0.052 [0.000, 0.117] | 0.778 [0.444, 1.000] | 0.778 [0.500, 1.000] | 0.902 [0.534, 1.000] | 0.902 [0.738, 1.000] | 100.0% | 1.000 [1.000, 1.000] |
| T04 | 2 | 0.128 [0.061, 0.178] | 0.128 [0.110, 0.150] | 0.333 [0.111, 0.667] | 0.333 [0.250, 0.400] | 0.853 [0.579, 0.962] | 0.853 [0.775, 0.949] | 100.0% | 1.000 [1.000, 1.000] |
| T05 | 2 | 0.042 [0.005, 0.086] | 0.042 [0.034, 0.050] | 0.800 [0.500, 1.000] | 0.800 [0.800, 0.800] | 0.975 [0.877, 1.000] | 0.975 [0.975, 1.000] | 100.0% | 1.000 [1.000, 1.000] |
| overall | 10 | 0.069 [0.044, 0.094] | 0.069 [0.045, 0.096] | 0.652 [0.522, 0.783] | 0.652 [0.512, 0.771] | 0.927 [0.861, 0.964] | 0.927 [0.862, 0.971] | 100.0% | 1.000 [1.000, 1.000] |

Direction has no stored item-level confidence interval; only its existing point estimate is shown. Threshold comparisons below are information only; no pre-registered threshold was changed.

| Metric | Preregistered threshold | Cluster lower bound | Lower bound alone meets threshold | Relevant bound meets threshold |
|---|---|---:|---|---|
| mae | at_most 0.150 | 0.045 | True | True (upper bound) |
| exact_band_accuracy | at_least 0.600 | 0.512 | False | False (lower bound) |
| spearman_rho | at_least 0.800 | 0.862 | True | True (lower bound) |
| direction_accuracy | at_least 0.900 | 1.000 | True | True (lower bound) |

For quiz gold, the evaluated trait set is the target trait only. Organic T01–T05, including gold-null unsupported-inference opportunities, and edge-case behavior are evaluated against their respective reference sets in the existing metrics. Quiz non-target traits and T06 are unassessed against gold.
