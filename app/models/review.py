from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator


class SeverityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    id: str = Field(..., description="Unique identifier for the finding (e.g. finding-001)")
    severity: SeverityEnum = Field(..., description="Severity level: critical, high, medium, low, info")
    title: str = Field(..., description="Short, plain language title of the finding")
    category: str = Field(default="general", description="Category such as security, correctness, performance, maintainability")
    description: str = Field(..., description="Clear explanation of the problem for non-experts")
    location: str = Field(default="global", description="Line number or scope location in code")
    why_it_matters: str = Field(..., description="Non-technical explanation of the risk or impact")
    recommendation: str = Field(..., description="Actionable code fix or recommended correction")
    verification_question: str = Field(..., description="Question to check user understanding of the finding")
    evidence: Optional[Any] = Field(default=None, description="Reserved for grounding service evidence attachment")


class ReviewRequest(BaseModel):
    artefact: str = Field(..., description="AI-generated code or artefact content to review")
    language: Optional[str] = Field(default=None, description="Programming language or format of the artefact")
    context: Optional[str] = Field(default=None, description="Optional background context or requirements")

    @field_validator("artefact")
    @classmethod
    def validate_artefact_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Artefact content cannot be empty or blank")
        return v


class ReviewResponse(BaseModel):
    status: str = Field(default="success", description="Status of the review process")
    summary: str = Field(..., description="High-level summary of review results")
    findings: List[Finding] = Field(default_factory=list, description="List of structured findings")
