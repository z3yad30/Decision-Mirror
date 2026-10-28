# Difficult cases

| Item | Severity | Error type | Expected | Actual | Notes |
|---|---|---|---|---|---|
| ORG01 | major | unsupported_inference | `null` | `0.7` | Gold T05 is annotated null. |
| ORG08 | major | context_confusion | `null` | `["financial_dependency", "financial_dependency"]` | Situational factor was missed or hallucinated. |
| Q01_A | major | missed_signal | `0.1` | `null` | Target trait T01 was null. |
| Q01_A | major | status_error | `"success"` | `"insufficient_evidence"` | Model extraction_status disagrees with gold-derived status. |
| Q07_C | major | missed_signal | `0.5` | `null` | Target trait T02 was null. |
| Q12_C | major | missed_signal | `0.5` | `null` | Target trait T03 was null. |
| Q20_B | major | missed_signal | `0.3` | `null` | Target trait T04 was null. |
| ORG01 | minor | score_deviation | `0.4` | `0.3` | T02 differs by 1 score band(s). |
| ORG07 | minor | score_deviation | `0.85` | `0.7` | T01 differs by 1 score band(s). |
| ORG08 | minor | score_deviation | `0.85` | `0.7` | T02 differs by 1 score band(s). |
| Q01_E | minor | score_deviation | `0.9` | `0.7` | T01 differs by 1 score band(s). |
| Q05_A | minor | score_deviation | `0.1` | `0.25` | T01 differs by 1 score band(s). |
| Q05_E | minor | score_deviation | `0.9` | `0.73` | T01 differs by 1 score band(s). |
| Q07_A | minor | score_deviation | `0.1` | `0.25` | T02 differs by 1 score band(s). |
| Q07_E | minor | score_deviation | `0.9` | `0.7` | T02 differs by 1 score band(s). |
| Q08_E | minor | score_deviation | `0.9` | `0.7` | T02 differs by 1 score band(s). |
| Q12_B | minor | score_deviation | `0.3` | `0.15` | T03 differs by 1 score band(s). |
| Q12_E | minor | score_deviation | `0.9` | `0.65` | T03 differs by 1 score band(s). |
| Q16_A | minor | score_deviation | `0.1` | `0.25` | T04 differs by 1 score band(s). |
| Q16_C | minor | score_deviation | `0.5` | `0.3` | T04 differs by 1 score band(s). |
| Q16_E | minor | score_deviation | `0.9` | `0.7` | T04 differs by 1 score band(s). |
| Q20_A | minor | score_deviation | `0.1` | `0.3` | T04 differs by 1 score band(s). |
| Q20_C | minor | score_deviation | `0.5` | `0.7` | T04 differs by 1 score band(s). |
| Q20_E | minor | score_deviation | `0.9` | `0.7` | T04 differs by 1 score band(s). |
| Q24_E | minor | score_deviation | `0.9` | `0.7` | T05 differs by 1 score band(s). |
| Q25_A | minor | score_deviation | `0.1` | `0.22` | T05 differs by 1 score band(s). |
| ORG07 | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| ORG16 | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q01_B | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q05_B | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q12_D | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q15_D | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q16_B | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q24_B | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q25_B | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q25_E | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |

## Cross-review sample

Items below matched the numeric gold band and are flagged for human evidence-support review; score agreement alone is not evidence quality.

- `Q05_B`
- `ORG07`
- `Q12_D`
- `Q25_E`
- `Q25_B`
- `Q01_B`
- `Q16_B`
- `ORG16`
- `Q15_D`
- `Q24_B`

## Ambiguous organic gold

- `ORG04`: reported separately, excluded from headline metrics.
- `ORG19`: reported separately, excluded from headline metrics.
