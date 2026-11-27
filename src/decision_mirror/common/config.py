from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # PROPOSED: minimum usable T06 observation count.
    t06_min_usable: int = Field(default=4, ge=0)
    # PROPOSED: T06 count at which the result is strong.
    t06_strong_at: int = Field(default=8, ge=0)
    # PROPOSED: pending decision reminder interval in days.
    reminder_days: int = Field(default=7, ge=0)
    # PROPOSED: weight multiplier for observations with a situational factor.
    situational_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    # PROPOSED: weight multiplier for quiz observations.
    quiz_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    # PROPOSED: fixed low confidence used for quiz observations.
    quiz_confidence: float = Field(default=0.30, ge=0.0, le=1.0)
    # PROPOSED: no recency decay in the first version.
    recency_half_life_days: float | None = Field(default=None, ge=0.0)
    # PROPOSED: placeholder shift window; calibrate in WP3/WP4.
    shift_window: int = Field(default=3, ge=0)
    # PROPOSED: placeholder shift threshold; calibrate in WP3/WP4.
    shift_threshold: float = Field(default=0.15, ge=0.0, le=1.0)

    def __init__(self, **data):
        for name in type(self).model_fields:
            key = f"DM_{name.upper()}"
            if name not in data and key in os.environ:
                data[name] = os.environ[key]
        super().__init__(**data)


settings = Settings()
