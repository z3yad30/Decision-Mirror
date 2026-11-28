# WP1: Shared Models and Configuration

Authored by: coding agent (lead run)
Date: 2026-11-27

## Models

| Model | Purpose |
|---|---|
| `TraitId` | Stable T01-T06 trait identifiers |
| `Source` | Quiz or decision observation source |
| `SessionStatus` | pending, approved, or rejected decision status |
| `SituationalCategory` | The eight contract situational categories |
| `SituationalFactor` | Decision-specific situational category and description |
| `TraitObservation` | Shared stored trait observation |
| `ExtractionTrait` | Trait shape used inside LLM output and pipeline envelopes |
| `ExtractionOutput` | Strict v1.0 LLM response shape |
| `ExtractionError` | Pipeline error detail |
| `ExtractionValidation` | Pipeline validation summary |
| `ExtractionResult` | Strict pipeline result envelope |
| `DecisionRecord` | Appendable decision and observation record |

## Examples

```json
{
  "decision_id": "D001",
  "extraction_status": "success",
  "traits": [
    {
      "trait_id": "T01",
      "trait_name": "Risk Tolerance",
      "score": 0.75,
      "confidence": 0.82,
      "evidence": ["I chose the startup"],
      "situational_factor": null,
      "context_notes": ""
    }
  ]
}
```

The `ExtractionOutput` example is intentionally a reduction of the contract for illustration; a real output contains exactly six ordered traits.

## Settings

| Setting | Default | Status | Override |
|---|---:|---|---|
| `t06_min_usable` | 4 | PROPOSED | `DM_T06_MIN_USABLE` |
| `t06_strong_at` | 8 | PROPOSED | `DM_T06_STRONG_AT` |
| `reminder_days` | 7 | PROPOSED | `DM_REMINDER_DAYS` |
| `situational_weight` | 0.5 | PROPOSED | `DM_SITUATIONAL_WEIGHT` |
| `quiz_weight` | 0.5 | PROPOSED | `DM_QUIZ_WEIGHT` |
| `quiz_confidence` | 0.30 | PROPOSED | `DM_QUIZ_CONFIDENCE` |
| `recency_half_life_days` | null | PROPOSED | `DM_RECENCY_HALF_LIFE_DAYS` |
| `shift_window` | 4 | PROPOSED | `DM_SHIFT_WINDOW` |
| `shift_threshold` | 0.15 | PROPOSED | `DM_SHIFT_THRESHOLD` |
