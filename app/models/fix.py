from pydantic import BaseModel, Field


class FixRequest(BaseModel):
    code: str = Field(..., description="Code containing the finding")
    finding_id: str = Field(..., description="Identifier of the finding to fix")
    finding_title: str = Field(..., description="Title of the finding to fix")
    language: str = Field(default="python", description="Programming language")


class FixResponse(BaseModel):
    status: str = Field(default="success")
    finding_id: str
    original_code: str
    fixed_code: str
    explanation: str