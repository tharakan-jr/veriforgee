from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.review import Finding, ReviewResponse


class VerifyRequest(BaseModel):
    original_code: str = Field(..., description="Original code before fix")
    fixed_code: str = Field(..., description="Modified/fixed code to verify")
    original_finding_title: Optional[str] = Field(default=None, description="Title of original finding to verify resolution")
    original_finding_id: Optional[str] = Field(default=None, description="ID of original finding")
    language: Optional[str] = Field(default=None, description="Programming language")


class VerifyResponse(BaseModel):
    status: str = Field(default="success", description="Verification status")
    is_resolved: bool = Field(..., description="True if the target issue was resolved")
    message: str = Field(..., description="Detailed verification status message")
    original_finding_title: str = Field(default="Security issue", description="Title of the checked finding")
    new_findings: List[Finding] = Field(default_factory=list, description="Findings detected in fixed code")
