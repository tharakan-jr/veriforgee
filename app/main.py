import os
from typing import Optional

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.api.v1.review import router as review_router
from app.api.v1.verify import router as verify_router
from app.api.v1.fix import router as fix_router
from app.grounding.router import router as grounding_router
from app import elevenlabs


app = FastAPI(
    title="VeriForge",
    description="AI-assisted review, explanation, grounding, and verification for non-expert builders.",
    version="0.1.0",
)


# API v1 Router
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(review_router)
api_v1_router.include_router(verify_router)
api_v1_router.include_router(fix_router)

app.include_router(api_v1_router)


# Grounding API
app.include_router(
    grounding_router,
    prefix="/ground",
    tags=["grounding"]
)


class VoiceExplainRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Beginner-friendly explanation text to convert to speech",
    )
    voice_id: Optional[str] = Field(
        default=None,
        description="Optional custom ElevenLabs voice ID override",
    )


@app.get("/health")
def health():
    """Application health probe."""
    return {"status": "ok"}


@app.get("/api/voice/status")
def voice_status():
    """
    Check ElevenLabs integration status.
    Returns whether the feature is configured without leaking API credentials.
    """
    status = elevenlabs.get_status()
    return {
        "status": "ok",
        "voice": status,
        "detail": (
            "Voice feature enabled and ready."
            if status["configured"]
            else "Voice feature optional/disabled (ELEVENLABS_API_KEY not set). Normal review features remain active."
        ),
    }


@app.post("/api/voice/explain")
def explain_voice(payload: VoiceExplainRequest):
    """
    Convert a review finding explanation to speech via backend ElevenLabs proxy.
    Returns audio/mpeg data.
    Gracefully handles missing keys and upstream API errors without breaking the review flow.
    """
    if not elevenlabs.is_configured():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Voice service unavailable",
                "message": (
                    "ELEVENLABS_API_KEY is not configured. Voice explanations are optional. "
                    "You can continue using the text-based review features, or set "
                    "ELEVENLABS_API_KEY in .env to enable audio."
                ),
                "available": False,
            },
        )

    try:
        audio_bytes = elevenlabs.synthesize_speech(
            text=payload.text,
            voice_id=payload.voice_id,
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="explanation.mp3"',
                "Cache-Control": "no-cache",
            },
        )
    except elevenlabs.ElevenLabsAPIError as exc:
        status_code = exc.status_code if 400 <= exc.status_code < 600 else 502
        raise HTTPException(
            status_code=status_code,
            detail={
                "error": "ElevenLabs API Error",
                "message": str(exc),
                "available": False,
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Voice Synthesis Failed",
                "message": f"Unexpected error while generating speech: {str(exc)}",
                "available": False,
            },
        ) from exc


# Static files mount
static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static"
    )


@app.get("/", response_class=HTMLResponse)
def home():
    """
    Landing page showcasing VeriForge core review workflow.
    """
    index_path = os.path.join(static_dir, "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path)

    return "<h1>VeriForge Backend Running</h1>"