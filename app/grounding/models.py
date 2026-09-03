"""
Pydantic models for the VeriForge grounding layer.

Request:  GroundingRequest
Response: GroundingResult  (grounded=True)  |  GroundingFailure (grounded=False)
"""

from pydantic import BaseModel, Field
from typing import Union


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class GroundingRequest(BaseModel):
    """
    Input from the review engine (or directly from the frontend).

    Fields
    ------
    category : str
        Normalised category label produced by the review engine, e.g.
        "sql_injection", "secrets", "xss".  Case-insensitive.
    keywords : list[str]
        Salient tokens extracted from the finding / code snippet, e.g.
        ["username", "query", "concatenation"].
    snippet : str
        The raw code snippet that triggered the finding (optional but
        improves the ``why_it_applies`` field in the response).
    """
    category: str = Field(..., description="Normalised finding category")
    keywords: list[str] = Field(default_factory=list, description="Salient tokens from the finding")
    snippet: str = Field(default="", description="Raw code snippet (optional)")


# ---------------------------------------------------------------------------
# Response — successful match
# ---------------------------------------------------------------------------

class GroundingSource(BaseModel):
    """Metadata for the authoritative source cited in a grounding result."""
    name: str = Field(..., description="Short display name of the source")
    title: str = Field(..., description="Full title of the specific document or section")
    url: str = Field(..., description="Canonical URL of the source")
    type: str = Field(..., description="Source type: 'official', 'standard', 'specification'")


class GroundingResult(BaseModel):
    """
    Returned when a finding can be reliably matched to an authoritative rule.
    """
    grounded: bool = Field(True, description="Always True for a successful match")
    rule_id: str = Field(..., description="Unique rule identifier, e.g. 'SEC-001'")
    title: str = Field(..., description="Human-readable rule title")
    category: str = Field(..., description="Rule category slug")
    cwe: str = Field(..., description="Primary CWE identifier, e.g. 'CWE-89'")
    source: GroundingSource
    evidence: str = Field(
        ...,
        description="A factual statement drawn from the authoritative source (no fabrication)"
    )
    why_it_applies: str = Field(
        ...,
        description="Explanation of why this rule applies to the submitted snippet/finding"
    )
    remediation: str = Field(..., description="Concrete remediation guidance")
    verification: str = Field(
        ...,
        description="How to verify the fix has been applied correctly"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Match confidence score between 0.0 and 1.0"
    )


# ---------------------------------------------------------------------------
# Response — no match
# ---------------------------------------------------------------------------

class GroundingFailure(BaseModel):
    """
    Returned when insufficient evidence exists to reliably match a rule.
    VeriForge MUST prefer this over a forced/hallucinated match.
    """
    grounded: bool = Field(False, description="Always False when no reliable match found")
    reason: str = Field(
        "Insufficient evidence to establish a reliable rule match",
        description="Human-readable explanation of why grounding failed"
    )


# ---------------------------------------------------------------------------
# Union type used by the router
# ---------------------------------------------------------------------------

GroundingResponse = Union[GroundingResult, GroundingFailure]
