"""
VeriForge Grounding — FastAPI Router
=====================================
Exposes: POST /ground

The route accepts a GroundingRequest and returns either a
GroundingResult (grounded=True) or a GroundingFailure (grounded=False).

API contract is intentionally simple so the review engine and the
frontend can call it identically.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.grounding.models import GroundingRequest, GroundingResult, GroundingFailure
from app.grounding.grounder import ground_from_request

router = APIRouter()


@router.post(
    "",
    summary="Ground a finding in an authoritative security rule",
    response_description=(
        "GroundingResult when a reliable rule match exists; "
        "GroundingFailure when evidence is insufficient."
    ),
    responses={
        200: {
            "description": "Grounding result (grounded may be true or false)",
            "content": {
                "application/json": {
                    "examples": {
                        "grounded": {
                            "summary": "Successful grounding",
                            "value": {
                                "grounded": True,
                                "rule_id": "SEC-001",
                                "title": "Hardcoded Credentials / Secrets",
                                "category": "secrets",
                                "cwe": "CWE-798",
                                "source": {
                                    "name": "OWASP Top 10:2025 — A07",
                                    "title": "A07:2025 – Identification and Authentication Failures",
                                    "url": "https://owasp.org/Top10/2025/A07_2025-Identification_and_Authentication_Failures/",
                                    "type": "official",
                                },
                                "evidence": "...",
                                "why_it_applies": "...",
                                "remediation": "...",
                                "verification": "...",
                                "confidence": 0.75,
                            },
                        },
                        "ungrounded": {
                            "summary": "No reliable match",
                            "value": {
                                "grounded": False,
                                "reason": "Insufficient evidence to establish a reliable rule match",
                            },
                        },
                    }
                }
            },
        },
    },
)
def ground_finding_endpoint(request: GroundingRequest) -> JSONResponse:
    """
    Ground a code-review finding against the VeriForge knowledge base.

    - **category**: normalised category slug from the review engine (e.g. `sql_injection`)
    - **keywords**: salient tokens extracted from the finding / snippet
    - **snippet**: optional raw code snippet for richer `why_it_applies` output

    Returns a `GroundingResult` when a rule can be reliably matched, or a
    `GroundingFailure` when the evidence is insufficient.

    VeriForge prefers `grounded=false` over hallucinated authority.
    """
    result = ground_from_request(request)
    return JSONResponse(content=result.model_dump())
