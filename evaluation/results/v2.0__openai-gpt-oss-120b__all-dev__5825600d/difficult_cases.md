# Difficult cases

| Item | Severity | Error type | Expected | Actual | Notes |
|---|---|---|---|---|---|
| ORG11 | critical | polarity_inversion | `0.6` | `0.15` | T02 lies on the opposite side of 0.5 by more than 0.2. |
| ORG11 | critical | score_deviation | `0.6` | `0.15` | T02 differs by 3 score band(s). |
| EDGE03 | major | edge_case_failure | `"insufficient_evidence"` | `"success"` | Edge expectation failed: status. |
| EDGE03 | major | edge_case_failure | `["T01", "T02", "T03", "T04", "T05", "T06"]` | `{"T01": null, "T02": null, "T03": null, "T04": null, "T05": 0.7, "T06": null}` | Edge expectation failed: null_traits. |
| EDGE04 | major | edge_case_failure | `["T02", "T03", "T04", "T05", "T06"]` | `{"T01": 0.7, "T02": null, "T03": 0.1, "T04": null, "T05": null, "T06": null}` | Edge expectation failed: null_traits. |
| EDGE04 | major | edge_case_failure | `null` | `{"T01": 0.7, "T02": null, "T03": 0.1, "T04": null, "T05": null, "T06": null}` | Edge expectation failed: max_confidence. |
| EDGE06 | major | edge_case_failure | `["T02", "T03", "T04", "T05", "T06"]` | `{"T01": 0.3, "T02": null, "T03": null, "T04": null, "T05": 0.3, "T06": null}` | Edge expectation failed: null_traits. |
| EDGE06 | major | edge_case_failure | `null` | `{"T01": 0.3, "T02": null, "T03": null, "T04": null, "T05": 0.3, "T06": null}` | Edge expectation failed: max_confidence. |
| EDGE09 | major | edge_case_failure | `["T01", "T03", "T04", "T06"]` | `{"T01": null, "T02": 0.7, "T03": null, "T04": 0.15, "T05": 0.7, "T06": null}` | Edge expectation failed: null_traits. |
| EDGE09 | major | edge_case_failure | `false` | `{"T01": null, "T02": 0.7, "T03": null, "T04": 0.15, "T05": 0.7, "T06": null}` | Edge expectation failed: situational_factor. |
| ORG02 | major | context_confusion | `null` | `["family_pressure", "family_pressure", "family_pressure"]` | Situational factor was missed or hallucinated. |
| ORG09 | major | context_confusion | `{"category": "low_stakes", "description": "Low-stakes social decision -- evidence is present but the decision's overall significance is minor, which should be reflected in lower weight during profile aggregation even though confidence in the extraction itself is moderate."}` | `["social_influence"]` | Detected situational factor category does not match gold. |
| ORG09 | major | unsupported_inference | `null` | `0.15` | Gold T05 is annotated null. |
| ORG11 | major | confidence_miscalibration | `"within 1 score band of 0.6"` | `0.15` | T02 confidence was 0.850 with an error of at least 2 bands. |
| ORG11 | major | context_confusion | `{"category": "other", "description": "Caregiving context noted but framed as a value, not merely a constraint -- raises confidence that this reflects a stable priority."}` | `["family_pressure", "family_pressure", "family_pressure"]` | Detected situational factor category does not match gold. |
| ORG11 | major | unsupported_inference | `null` | `0.15` | Gold T05 is annotated null. |
| ORG12 | major | context_confusion | `{"category": "low_stakes", "description": "Extremely low-stakes decision; should contribute minimally to the running profile despite a clear directional signal."}` | `["social_influence"]` | Detected situational factor category does not match gold. |
| ORG14 | major | evidence_not_grounded | `"evidence quote grounded in decision_text"` | `"\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""` | T01 evidence quote was not found after quote, whitespace, and case normalization. |
| ORG14 | major | evidence_not_grounded | `"evidence quote grounded in decision_text"` | `"\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""` | T02 evidence quote was not found after quote, whitespace, and case normalization. |
| ORG14 | major | evidence_not_grounded | `"evidence quote grounded in decision_text"` | `"\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""` | T03 evidence quote was not found after quote, whitespace, and case normalization. |
| ORG14 | major | evidence_not_grounded | `"evidence quote grounded in decision_text"` | `"\"turned down three promotions in a row because each one would have meant more travel and less time with my kids\""` | T05 evidence quote was not found after quote, whitespace, and case normalization. |
| ORG14 | major | unsupported_inference | `null` | `0.3` | Gold T01 is annotated null. |
| ORG14 | major | unsupported_inference | `null` | `0.15` | Gold T02 is annotated null. |
| ORG14 | major | unsupported_inference | `null` | `0.25` | Gold T05 is annotated null. |
| ORG17 | major | unsupported_inference | `null` | `0.7` | Gold T03 is annotated null. |
| ORG20 | major | context_confusion | `null` | `["financial_dependency"]` | Situational factor was missed or hallucinated. |
| ORG20 | major | missed_signal | `0.35` | `null` | Gold T01 score is non-null but model score is null. |
| ORG20 | major | missed_signal | `0.7` | `null` | Gold T05 score is non-null but model score is null. |
| Q04_C | major | missed_signal | `0.5` | `null` | Target trait T01 was null. |
| Q04_C | major | status_error | `"success"` | `"insufficient_evidence"` | Model extraction_status disagrees with gold-derived status. |
| Q19_C | major | missed_signal | `0.5` | `null` | Target trait T04 was null. |
| ORG02 | minor | score_deviation | `0.8` | `0.78` | T03 differs by 1 score band(s). |
| ORG03 | minor | score_deviation | `0.1` | `0.3` | T04 differs by 1 score band(s). |
| ORG03 | minor | score_deviation | `0.9` | `0.75` | T05 differs by 1 score band(s). |
| ORG09 | minor | score_deviation | `0.25` | `0.15` | T03 differs by 1 score band(s). |
| ORG12 | minor | score_deviation | `0.2` | `0.15` | T03 differs by 1 score band(s). |
| ORG13 | minor | score_deviation | `0.9` | `0.7` | T04 differs by 1 score band(s). |
| ORG20 | minor | score_deviation | `0.85` | `0.7` | T02 differs by 1 score band(s). |
| Q02_A | minor | score_deviation | `0.1` | `0.3` | T01 differs by 1 score band(s). |
| Q02_E | minor | score_deviation | `0.9` | `0.7` | T01 differs by 1 score band(s). |
| Q03_A | minor | score_deviation | `0.1` | `0.3` | T01 differs by 1 score band(s). |
| Q03_D | minor | score_deviation | `0.7` | `0.55` | T01 differs by 1 score band(s). |
| Q03_E | minor | score_deviation | `0.9` | `0.7` | T01 differs by 1 score band(s). |
| Q04_A | minor | score_deviation | `0.1` | `0.3` | T01 differs by 1 score band(s). |
| Q04_E | minor | score_deviation | `0.9` | `0.7` | T01 differs by 1 score band(s). |
| Q06_E | minor | score_deviation | `0.9` | `0.7` | T02 differs by 1 score band(s). |
| Q09_A | minor | score_deviation | `0.1` | `0.3` | T02 differs by 1 score band(s). |
| Q09_E | minor | score_deviation | `0.9` | `0.72` | T02 differs by 1 score band(s). |
| Q10_A | minor | score_deviation | `0.1` | `0.3` | T02 differs by 1 score band(s). |
| Q10_E | minor | score_deviation | `0.9` | `0.7` | T02 differs by 1 score band(s). |
| Q11_B | minor | score_deviation | `0.3` | `0.15` | T03 differs by 1 score band(s). |
| Q13_E | minor | score_deviation | `0.9` | `0.7` | T03 differs by 1 score band(s). |
| Q17_A | minor | score_deviation | `0.1` | `0.3` | T04 differs by 1 score band(s). |
| Q17_C | minor | score_deviation | `0.5` | `0.7` | T04 differs by 1 score band(s). |
| Q18_A | minor | score_deviation | `0.1` | `0.3` | T04 differs by 1 score band(s). |
| Q18_C | minor | score_deviation | `0.5` | `0.3` | T04 differs by 1 score band(s). |
| Q18_E | minor | score_deviation | `0.9` | `0.7` | T04 differs by 1 score band(s). |
| Q19_A | minor | score_deviation | `0.1` | `0.3` | T04 differs by 1 score band(s). |
| Q19_E | minor | score_deviation | `0.9` | `0.7` | T04 differs by 1 score band(s). |
| Q21_B | minor | score_deviation | `0.3` | `0.1` | T05 differs by 1 score band(s). |
| Q21_E | minor | score_deviation | `0.9` | `0.7` | T05 differs by 1 score band(s). |
| Q23_B | minor | score_deviation | `0.3` | `0.15` | T05 differs by 1 score band(s). |
| ORG11 | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q02_C | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q02_D | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q03_B | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q06_C | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q06_D | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q09_C | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q19_B | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q21_C | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |
| Q22_C | review | needs_manual_review | `"human review of evidence support"` | `"target score in exact gold band"` | Sampled for independent cross-review; numeric score match does not establish evidence support. |

## Cross-review sample

Items below matched the numeric gold band and are flagged for human evidence-support review; score agreement alone is not evidence quality.

- `Q19_B`
- `Q02_D`
- `ORG11`
- `Q22_C`
- `Q09_C`
- `Q06_D`
- `Q06_C`
- `Q03_B`
- `Q02_C`
- `Q21_C`

## Ambiguous organic gold

- `ORG05`: reported separately, excluded from headline metrics.
- `ORG10`: reported separately, excluded from headline metrics.
- `ORG15`: reported separately, excluded from headline metrics.
- `ORG18`: reported separately, excluded from headline metrics.
