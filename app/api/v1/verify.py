from fastapi import APIRouter, HTTPException, status
from app.models.verify import VerifyRequest, VerifyResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/verify", tags=["Review Engine Verification"])


@router.post(
    "",
    response_model=VerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify if a finding was resolved in modified code",
    description="Runs the modified/fixed code through the review engine and compares findings against the original finding to confirm resolution."
)
async def verify_fix(payload: VerifyRequest) -> VerifyResponse:
    if not payload.fixed_code or not payload.fixed_code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fixed code content cannot be empty."
        )

    service = ReviewService()
    try:
        review_result = await service.review_artefact(
            artefact=payload.fixed_code,
            language=payload.language
        )

        target_title = (payload.original_finding_title or "").lower().strip()
        
        # Check if the original issue title/category is present in new findings
        issue_still_present = False
        matching_finding = None

        for f in review_result.findings:
            # Skip info "Code structure looks clear" finding
            if f.severity == "info" and "clear" in f.title.lower():
                continue

            if target_title and target_title in f.title.lower():
                issue_still_present = True
                matching_finding = f
                break
            elif not target_title and f.severity in ["critical", "high", "medium"]:
                issue_still_present = True
                matching_finding = f
                break

        if issue_still_present:
            is_resolved = False
            message = f"Issue still detected: {matching_finding.title if matching_finding else 'Security vulnerability present'}."
        else:
            is_resolved = True
            message = f"Issue resolved: The original issue '{payload.original_finding_title or 'security vulnerability'}' is no longer detected."

        return VerifyResponse(
            status="success",
            is_resolved=is_resolved,
            message=message,
            original_finding_title=payload.original_finding_title or "Security finding",
            new_findings=review_result.findings
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying fixed code: {str(e)}"
        )
