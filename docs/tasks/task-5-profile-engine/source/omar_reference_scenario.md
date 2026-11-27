# Omar reference scenario

Authored by: coding agent (lead run) — 2026-11-27

This is a fully synthetic reference history for user `SYN_OMAR`. Every decision
record below is invented, is marked `synthetic: true`, and describes no real
person or event. Descriptions were checked with normalized substring matching
against the scenario/answer text in `quiz_gold_v1.0.json` and the decision text
in `organic_gold_v1.0.json` and `edge_cases_v1.0.json`; no description matched.

All nine decisions are approved and have strictly ascending dates in the past.
Each numeric trait entry is `score / confidence`. Confidence is recorded for
completeness but is not part of the T06 calculation. A null score has confidence
`0.0` and includes its reason.

| ID | Date | Synthetic description | Status | Synthetic | T01 score / confidence | T02 score / confidence | T03 score / confidence | T04 score / confidence | T05 score / confidence | Situational factor |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| SYN_OMAR_01 | 2024-02-11 | I took a smaller workshop room after comparing several lease terms. | approved | true | 0.43 / 0.82 | 0.34 / 0.78 | 0.30 / 0.72 | 0.62 / 0.81 | 0.40 / 0.75 | No |
| SYN_OMAR_02 | 2024-04-03 | I booked a mountain lodge only after reviewing the cancellation options. | approved | true | 0.48 / 0.84 | 0.41 / 0.80 | 0.40 / 0.76 | 0.58 / 0.79 | 0.45 / 0.78 | No |
| SYN_OMAR_03 | 2024-07-22 | I replaced an aging screen with a refurbished unit after testing samples. | approved | true | 0.52 / 0.86 | 0.48 / 0.82 | 0.50 / 0.80 | 0.60 / 0.83 | 0.50 / 0.81 | No |
| SYN_OMAR_04 | 2024-10-14 | I delayed a neighborhood planting plot until the annual fee was confirmed. | approved | true | 0.57 / 0.88 | 0.55 / 0.84 | 0.60 / 0.82 | 0.56 / 0.85 | 0.55 / 0.83 | No |
| SYN_OMAR_05 | 2025-01-08 | A rail service interruption reshaped my route choice for the regional fair. | approved | true | 0.16 / 0.70 | 0.61 / 0.70 | 0.65 / 0.70 | 0.55 / 0.70 | 0.61 / 0.70 | Yes — `external_constraint`: A temporary rail disruption limited the available routes. |
| SYN_OMAR_06 | 2025-03-17 | I chose a flexible evening course instead of the fixed-term cohort. | approved | true | 0.19 / 0.76 | 0.63 / 0.77 | 0.65 / 0.78 | 0.49 / 0.79 | 0.64 / 0.78 | No |
| SYN_OMAR_07 | 2025-06-02 | I scheduled a repair visit after the replacement parts arrived. | approved | true | 0.24 / 0.78 | 0.66 / 0.79 | 0.70 / 0.80 | 0.46 / 0.81 | 0.60 / 0.80 | No |
| SYN_OMAR_08 | 2025-09-11 | I shared a workroom to keep the recurring monthly cost manageable. | approved | true | 0.29 / 0.80 | 0.69 / 0.81 | 0.75 / 0.82 | 0.42 / 0.83 | 0.57 / 0.82 | No |
| SYN_OMAR_09 | 2026-02-26 | I returned to one project outline after comparing notes from earlier attempts. | approved | true | 0.34 / 0.82 | 0.72 / 0.83 | null / 0.0 — The narrative does not provide evidence relevant to T03. | 0.38 / 0.84 | 0.53 / 0.84 | No |

## T06 checkpoints

T06 uses only approved, non-null, non-situational scores. The population
standard deviation is used:

`T06 = 1 - 2 × population_SD(scores)`, where
`population_SD = sqrt(sum((score - mean)^2) / usable_count)`.

Values below are rounded to two decimals. The usable count is shown separately
for every trait.

| Trait | 4-decision checkpoint: T06 (usable count) | 9-decision checkpoint: T06 (usable count) |
|---|---:|---:|
| T01 | 0.90 (4) | 0.74 (8) |
| T02 | 0.84 (4) | 0.74 (8) |
| T03 | 0.78 (4) | 0.70 (7) |
| T04 | 0.96 (4) | 0.83 (8) |
| T05 | 0.89 (4) | 0.85 (8) |

### Exclusions

- At the 4-decision checkpoint, no decision is excluded: decisions 1–4 are
  approved, non-situational, and have non-null scores for all five traits.
- At the 9-decision checkpoint, `SYN_OMAR_05` is excluded for every trait
  because it carries a situational factor. `SYN_OMAR_09` is additionally
  excluded for T03 only because its T03 score is null. It remains usable for
  T01, T02, T04, and T05.
- No decision is pending or rejected; therefore none is excluded for status.

### Hand calculation

The following values were computed in a throwaway Python script outside the
repository. `sum_sq` is `sum((score - mean)^2)`; the population variance is
`sum_sq / n`.

**4-decision checkpoint**

- T01 scores `[0.43, 0.48, 0.52, 0.57]`: sum `2.00`; mean `0.50000000`;
  sum_sq `0.0106000000`; variance `0.0026500000`; SD `0.0514781507`;
  `1 - 2 × 0.0514781507 = 0.8970436986` → **0.90**.
- T02 scores `[0.34, 0.41, 0.48, 0.55]`: sum `1.78`; mean `0.44500000`;
  sum_sq `0.0245000000`; variance `0.0061250000`; SD `0.0782623792`;
  `1 - 2 × 0.0782623792 = 0.8434752416` → **0.84**.
- T03 scores `[0.30, 0.40, 0.50, 0.60]`: sum `1.80`; mean `0.45000000`;
  sum_sq `0.0500000000`; variance `0.0125000000`; SD `0.1118033989`;
  `1 - 2 × 0.1118033989 = 0.7763932023` → **0.78**.
- T04 scores `[0.62, 0.58, 0.60, 0.56]`: sum `2.36`; mean `0.59000000`;
  sum_sq `0.0020000000`; variance `0.0005000000`; SD `0.0223606798`;
  `1 - 2 × 0.0223606798 = 0.9552786405` → **0.96**.
- T05 scores `[0.40, 0.45, 0.50, 0.55]`: sum `1.90`; mean `0.47500000`;
  sum_sq `0.0125000000`; variance `0.0031250000`; SD `0.0559016994`;
  `1 - 2 × 0.0559016994 = 0.8881966011` → **0.89**.

**9-decision checkpoint**

- T01 usable scores `[0.43, 0.48, 0.52, 0.57, 0.19, 0.24, 0.29, 0.34]`:
  sum `3.06`; mean `0.38250000`; sum_sq `0.1335500000`;
  variance `0.0166937500`; SD `0.1292042956`;
  `1 - 2 × 0.1292042956 = 0.7415914088` → **0.74**.
- T02 usable scores `[0.34, 0.41, 0.48, 0.55, 0.63, 0.66, 0.69, 0.72]`:
  sum `4.48`; mean `0.56000000`; sum_sq `0.1348000000`;
  variance `0.0168500000`; SD `0.1298075499`;
  `1 - 2 × 0.1298075499 = 0.7403849003` → **0.74**.
- T03 usable scores `[0.30, 0.40, 0.50, 0.60, 0.65, 0.70, 0.75]`:
  sum `3.90`; mean `0.55714286`; sum_sq `0.1621428571`;
  variance `0.0231632653`; SD `0.1521948268`;
  `1 - 2 × 0.1521948268 = 0.6956103464` → **0.70**.
- T04 usable scores `[0.62, 0.58, 0.60, 0.56, 0.49, 0.46, 0.42, 0.38]`:
  sum `4.11`; mean `0.51375000`; sum_sq `0.0553875000`;
  variance `0.0069234375`; SD `0.0832071962`;
  `1 - 2 × 0.0832071962 = 0.8335856076` → **0.83**.
- T05 usable scores `[0.40, 0.45, 0.50, 0.55, 0.64, 0.60, 0.57, 0.53]`:
  sum `4.24`; mean `0.53000000`; sum_sq `0.0432000000`;
  variance `0.0054000000`; SD `0.0734846923`;
  `1 - 2 × 0.0734846923 = 0.8530306154` → **0.85**.

### Shift example

For T01, the first four usable scores average `0.500`; the later four usable
scores (decisions 6–9) average `0.265`. Their absolute mean difference is
`|0.265 - 0.500| = 0.235`. For this scenario check only, a four-observation
window and an illustrative threshold of `0.20` produce an expected shift flag:
`0.235 >= 0.20`. This is not a project-wide threshold calibration.

## Machine-readable scenario

```json
{
  "user_id": "SYN_OMAR",
  "synthetic": true,
  "decisions": [
    {
      "id": "SYN_OMAR_01",
      "date": "2024-02-11",
      "description": "I took a smaller workshop room after comparing several lease terms.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.43, "confidence": 0.82},
        "T02": {"score": 0.34, "confidence": 0.78},
        "T03": {"score": 0.30, "confidence": 0.72},
        "T04": {"score": 0.62, "confidence": 0.81},
        "T05": {"score": 0.40, "confidence": 0.75}
      },
      "situational_factor": null
    },
    {
      "id": "SYN_OMAR_02",
      "date": "2024-04-03",
      "description": "I booked a mountain lodge only after reviewing the cancellation options.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.48, "confidence": 0.84},
        "T02": {"score": 0.41, "confidence": 0.80},
        "T03": {"score": 0.40, "confidence": 0.76},
        "T04": {"score": 0.58, "confidence": 0.79},
        "T05": {"score": 0.45, "confidence": 0.78}
      },
      "situational_factor": null
    },
    {
      "id": "SYN_OMAR_03",
      "date": "2024-07-22",
      "description": "I replaced an aging screen with a refurbished unit after testing samples.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.52, "confidence": 0.86},
        "T02": {"score": 0.48, "confidence": 0.82},
        "T03": {"score": 0.50, "confidence": 0.80},
        "T04": {"score": 0.60, "confidence": 0.83},
        "T05": {"score": 0.50, "confidence": 0.81}
      },
      "situational_factor": null
    },
    {
      "id": "SYN_OMAR_04",
      "date": "2024-10-14",
      "description": "I delayed a neighborhood planting plot until the annual fee was confirmed.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.57, "confidence": 0.88},
        "T02": {"score": 0.55, "confidence": 0.84},
        "T03": {"score": 0.60, "confidence": 0.82},
        "T04": {"score": 0.56, "confidence": 0.85},
        "T05": {"score": 0.55, "confidence": 0.83}
      },
      "situational_factor": null
    },
    {
      "id": "SYN_OMAR_05",
      "date": "2025-01-08",
      "description": "A rail service interruption reshaped my route choice for the regional fair.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.16, "confidence": 0.70},
        "T02": {"score": 0.61, "confidence": 0.70},
        "T03": {"score": 0.65, "confidence": 0.70},
        "T04": {"score": 0.55, "confidence": 0.70},
        "T05": {"score": 0.61, "confidence": 0.70}
      },
      "situational_factor": {
        "category": "external_constraint",
        "description": "A temporary rail disruption limited the available routes."
      }
    },
    {
      "id": "SYN_OMAR_06",
      "date": "2025-03-17",
      "description": "I chose a flexible evening course instead of the fixed-term cohort.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.19, "confidence": 0.76},
        "T02": {"score": 0.63, "confidence": 0.77},
        "T03": {"score": 0.65, "confidence": 0.78},
        "T04": {"score": 0.49, "confidence": 0.79},
        "T05": {"score": 0.64, "confidence": 0.78}
      },
      "situational_factor": null
    },
    {
      "id": "SYN_OMAR_07",
      "date": "2025-06-02",
      "description": "I scheduled a repair visit after the replacement parts arrived.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.24, "confidence": 0.78},
        "T02": {"score": 0.66, "confidence": 0.79},
        "T03": {"score": 0.70, "confidence": 0.80},
        "T04": {"score": 0.46, "confidence": 0.81},
        "T05": {"score": 0.60, "confidence": 0.80}
      },
      "situational_factor": null
    },
    {
      "id": "SYN_OMAR_08",
      "date": "2025-09-11",
      "description": "I shared a workroom to keep the recurring monthly cost manageable.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.29, "confidence": 0.80},
        "T02": {"score": 0.69, "confidence": 0.81},
        "T03": {"score": 0.75, "confidence": 0.82},
        "T04": {"score": 0.42, "confidence": 0.83},
        "T05": {"score": 0.57, "confidence": 0.82}
      },
      "situational_factor": null
    },
    {
      "id": "SYN_OMAR_09",
      "date": "2026-02-26",
      "description": "I returned to one project outline after comparing notes from earlier attempts.",
      "status": "approved",
      "synthetic": true,
      "traits": {
        "T01": {"score": 0.34, "confidence": 0.82},
        "T02": {"score": 0.72, "confidence": 0.83},
        "T03": {
          "score": null,
          "confidence": 0.0,
          "null_reason": "The narrative does not provide evidence relevant to T03."
        },
        "T04": {"score": 0.38, "confidence": 0.84},
        "T05": {"score": 0.53, "confidence": 0.84}
      },
      "situational_factor": null
    }
  ],
  "checkpoints": {
    "4": {
      "traits": {
        "T01": {"value": 0.90, "usable_count": 4},
        "T02": {"value": 0.84, "usable_count": 4},
        "T03": {"value": 0.78, "usable_count": 4},
        "T04": {"value": 0.96, "usable_count": 4},
        "T05": {"value": 0.89, "usable_count": 4}
      },
      "excluded_decisions": []
    },
    "9": {
      "traits": {
        "T01": {"value": 0.74, "usable_count": 8},
        "T02": {"value": 0.74, "usable_count": 8},
        "T03": {"value": 0.70, "usable_count": 7},
        "T04": {"value": 0.83, "usable_count": 8},
        "T05": {"value": 0.85, "usable_count": 8}
      },
      "excluded_decisions": [
        {
          "id": "SYN_OMAR_05",
          "traits": ["T01", "T02", "T03", "T04", "T05"],
          "reason": "situational_factor is non-null"
        },
        {
          "id": "SYN_OMAR_09",
          "traits": ["T03"],
          "reason": "T03 score is null"
        }
      ]
    }
  }
}
```
