from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TraitId(str, Enum):
    T01 = "T01"
    T02 = "T02"
    T03 = "T03"
    T04 = "T04"
    T05 = "T05"
    T06 = "T06"


class Source(str, Enum):
    QUIZ = "quiz"
    DECISION = "decision"


class SessionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SituationalCategory(str, Enum):
    FINANCIAL_DEPENDENCY = "financial_dependency"
    FAMILY_PRESSURE = "family_pressure"
    EXTERNAL_DEADLINE = "external_deadline"
    EXTERNAL_CONSTRAINT = "external_constraint"
    LIMITED_ALTERNATIVES = "limited_alternatives"
    SOCIAL_INFLUENCE = "social_influence"
    LOW_STAKES = "low_stakes"
    OTHER = "other"


class SituationalFactor(StrictModel):
    category: SituationalCategory
    description: str


class TraitObservation(StrictModel):
    trait_id: TraitId
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str]
    situational_factor: Optional[SituationalFactor] = None
    context_notes: str
    source: Source

    @model_validator(mode="after")
    def validate_score_support(self) -> "TraitObservation":
        if self.score is None:
            if self.confidence != 0.0:
                raise ValueError("null score requires confidence 0.0")
            if self.evidence:
                raise ValueError("null score requires empty evidence")
        elif not self.evidence:
            raise ValueError("non-null score requires at least one evidence item")
        return self


TRAIT_NAMES = {
    TraitId.T01: "Risk Tolerance",
    TraitId.T02: "Time Horizon",
    TraitId.T03: "Locus of Priority",
    TraitId.T04: "Decisiveness Speed",
    TraitId.T05: "Emotional vs. Analytical Weighting",
    TraitId.T06: "Self-Consistency",
}


class ExtractionTrait(StrictModel):
    trait_id: TraitId
    trait_name: str
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str]
    situational_factor: Optional[SituationalFactor] = None
    context_notes: str

    @model_validator(mode="after")
    def validate_trait_contract(self) -> "ExtractionTrait":
        if TRAIT_NAMES[self.trait_id] != self.trait_name:
            raise ValueError("trait_name must match trait_id")
        if self.score is None:
            if self.confidence != 0.0:
                raise ValueError("null score requires confidence 0.0")
            if self.evidence:
                raise ValueError("null score requires empty evidence")
            if self.trait_id != TraitId.T06 and not self.context_notes.strip():
                raise ValueError("null T01-T05 score requires explanatory context_notes")
        elif not self.evidence:
            raise ValueError("non-null score requires at least one evidence item")
        return self


class ExtractionOutput(StrictModel):
    decision_id: str = Field(pattern=r"^[A-Za-z0-9_.\-]{1,64}$")
    extraction_status: str
    traits: list[ExtractionTrait]

    @model_validator(mode="after")
    def validate_output_contract(self) -> "ExtractionOutput":
        if self.extraction_status not in ("success", "insufficient_evidence"):
            raise ValueError("model-emitted error status is invalid")
        if len(self.traits) != 6:
            raise ValueError("exactly six traits are required")
        if [trait.trait_id for trait in self.traits] != [
            TraitId.T01,
            TraitId.T02,
            TraitId.T03,
            TraitId.T04,
            TraitId.T05,
            TraitId.T06,
        ]:
            raise ValueError("traits must be exactly T01-T06 in order")
        if self.traits[5].score is not None:
            raise ValueError("T06 must be null without history")
        has_score = any(trait.score is not None for trait in self.traits)
        if self.extraction_status == "success" and not has_score:
            raise ValueError("success requires at least one non-null score")
        if self.extraction_status == "insufficient_evidence" and has_score:
            raise ValueError("insufficient_evidence requires all scores to be null")
        return self


class ExtractionError(StrictModel):
    type: str
    message: str

    @model_validator(mode="after")
    def validate_error_type(self) -> "ExtractionError":
        allowed = {
            "empty_response",
            "not_json",
            "schema_violation",
            "semantic_violation",
            "api_error",
        }
        if self.type not in allowed:
            raise ValueError("unknown extraction error type")
        return self


class ExtractionValidation(StrictModel):
    schema_valid: bool
    semantic_valid: bool
    warnings: list[str]


class ExtractionResult(StrictModel):
    decision_id: str = Field(pattern=r"^[A-Za-z0-9_.\-]{1,64}$")
    extraction_status: str
    traits: Optional[list[ExtractionTrait]] = None
    model_version: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    prompt_sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    error: Optional[ExtractionError] = None
    validation: ExtractionValidation

    @model_validator(mode="after")
    def validate_envelope_contract(self) -> "ExtractionResult":
        if self.extraction_status not in ("success", "insufficient_evidence", "error"):
            raise ValueError("unknown extraction_status")
        if self.extraction_status == "error":
            if self.traits is not None or self.error is None:
                raise ValueError("error envelopes require traits=null and an error")
        elif self.traits is None or self.error is not None:
            raise ValueError("non-error envelopes require traits and error=null")
        else:
            if len(self.traits) != 6:
                raise ValueError("exactly six traits are required")
            if [trait.trait_id for trait in self.traits] != [
                TraitId.T01,
                TraitId.T02,
                TraitId.T03,
                TraitId.T04,
                TraitId.T05,
                TraitId.T06,
            ]:
                raise ValueError("traits must be exactly T01-T06 in order")
            if self.traits[5].score is not None:
                raise ValueError("T06 must be null without history")
            has_score = any(trait.score is not None for trait in self.traits)
            if self.extraction_status == "success" and not has_score:
                raise ValueError("success requires at least one non-null score")
            if self.extraction_status == "insufficient_evidence" and has_score:
                raise ValueError("insufficient_evidence requires all scores to be null")
        return self


class DecisionRecord(StrictModel):
    decision_id: str = Field(pattern=r"^[A-Za-z0-9_.\-]{1,64}$")
    user_id: str
    session_id: str
    decision_text: str
    decision_date: date
    approval_date: Optional[date] = None
    status: SessionStatus
    observations: list[TraitObservation]
    prompt_version: str
    prompt_sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    model_version: str
    advisor_top_choice_approved: Optional[bool] = None
    synthetic: bool = False
