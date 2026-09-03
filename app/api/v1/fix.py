from fastapi import APIRouter, HTTPException, status

from app.models.fix import FixRequest, FixResponse
from app.services.llm.factory import get_llm_provider

router = APIRouter(prefix="/fix", tags=["Review Engine Fixes"])


@router.post("", response_model=FixResponse, status_code=status.HTTP_200_OK)
async def propose_fix(payload: FixRequest) -> FixResponse:
    if not payload.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code content cannot be empty.")

    provider = get_llm_provider()
    generate_remediation = getattr(provider, "generate_remediation", None)
    if generate_remediation is None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="This LLM provider does not support fixes yet.")

    try:
        fixed_code = await generate_remediation(payload.code, payload.finding_title, payload.language)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating fix: {exc}") from exc

    if fixed_code.strip() == payload.code.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Generated fix did not change the original code.")

    return FixResponse(
        finding_id=payload.finding_id,
        original_code=payload.code,
        fixed_code=fixed_code,
        explanation=f"Applied a deterministic remediation for {payload.finding_title}.",
    )