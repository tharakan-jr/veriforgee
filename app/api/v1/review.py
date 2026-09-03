from fastapi import APIRouter, HTTPException, status
from app.models.review import ReviewRequest, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/review", tags=["Review Engine"])


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze AI-generated artefact",
    description="Submits an AI-generated code artefact for structured evaluation, plain language explanation, grounding design, and understanding verification."
)
async def review_code(payload: ReviewRequest) -> ReviewResponse:
    if not payload.artefact or not payload.artefact.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artefact content cannot be empty."
        )

    service = ReviewService()
    try:
        response = await service.review_artefact(
            artefact=payload.artefact,
            language=payload.language,
            context=payload.context
        )
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred during review analysis: {str(e)}"
        )
