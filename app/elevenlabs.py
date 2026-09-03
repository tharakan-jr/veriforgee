"""
ElevenLabs Text-to-Speech service module for VeriForge.

Provides optional voice explanation functionality with safe credential handling,
graceful fallbacks when unconfigured, and error isolation.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

# Default configuration
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel: clear, articulate, beginner-friendly
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class ElevenLabsError(Exception):
    """Base exception for ElevenLabs integration errors."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class ElevenLabsNotConfiguredError(ElevenLabsError):
    """Raised when ELEVENLABS_API_KEY is missing or empty."""

    def __init__(self, message: str = "ELEVENLABS_API_KEY is not configured in environment."):
        super().__init__(message, status_code=503)


class ElevenLabsAPIError(ElevenLabsError):
    """Raised when upstream ElevenLabs API returns an error or fails."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code=status_code)


def get_api_key() -> Optional[str]:
    """Retrieve the ElevenLabs API key from environment variables."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    return key if key else None


def is_configured() -> bool:
    """Return True if ElevenLabs API key is present in environment."""
    return get_api_key() is not None


def get_default_voice_id() -> str:
    """Return default voice ID from environment or fallback default."""
    return os.environ.get("ELEVENLABS_VOICE_ID", "").strip() or DEFAULT_VOICE_ID


def get_default_model_id() -> str:
    """Return default model ID from environment or fallback default."""
    return os.environ.get("ELEVENLABS_MODEL_ID", "").strip() or DEFAULT_MODEL_ID


def get_status() -> Dict[str, Any]:
    """
    Return voice service status metadata safely.
    NEVER exposes the API key.
    """
    configured = is_configured()
    return {
        "configured": configured,
        "available": configured,
        "voice_id": get_default_voice_id(),
        "model_id": get_default_model_id(),
    }


def _sanitize_error(message: str, api_key: Optional[str] = None) -> str:
    """Ensure sensitive credentials never appear in error messages."""
    if api_key and api_key in message:
        message = message.replace(api_key, "[REDACTED]")
    return message


def synthesize_speech(
    text: str,
    voice_id: Optional[str] = None,
    model_id: Optional[str] = None,
    timeout_seconds: int = 15,
) -> bytes:
    """
    Synthesize text into speech using ElevenLabs API.

    Args:
        text: Plain-language explanation to convert to speech.
        voice_id: Optional voice ID override.
        model_id: Optional model ID override.
        timeout_seconds: Timeout for network request.

    Returns:
        bytes: Raw MP3 audio data.

    Raises:
        ElevenLabsNotConfiguredError: If API key is not set.
        ElevenLabsAPIError: If ElevenLabs API request fails.
        ValueError: If text is empty.
    """
    api_key = get_api_key()
    if not api_key:
        raise ElevenLabsNotConfiguredError(
            "ELEVENLABS_API_KEY is not set. Voice explanation is optional; "
            "set ELEVENLABS_API_KEY in your .env file to enable it."
        )

    clean_text = text.strip() if text else ""
    if not clean_text:
        raise ValueError("Text to synthesize cannot be empty.")

    selected_voice = voice_id.strip() if voice_id and voice_id.strip() else get_default_voice_id()
    selected_model = model_id.strip() if model_id and model_id.strip() else get_default_model_id()

    url = ELEVENLABS_TTS_URL.format(voice_id=selected_voice)
    payload_dict = {
        "text": clean_text,
        "model_id": selected_model,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }
    payload_bytes = json.dumps(payload_dict).encode("utf-8")

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
        "User-Agent": "VeriForge/0.1.0",
    }

    req = urllib.request.Request(url, data=payload_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raw_error = ""
        try:
            raw_error = exc.read().decode("utf-8", errors="replace")
            error_data = json.loads(raw_error)
            detail = (
                error_data.get("detail", {}).get("message")
                or error_data.get("detail")
                or str(error_data)
            )
        except Exception:
            detail = f"HTTP {exc.code} ({exc.reason})"

        sanitized_detail = _sanitize_error(str(detail), api_key)
        raise ElevenLabsAPIError(
            f"ElevenLabs API returned HTTP {exc.code}: {sanitized_detail}",
            status_code=exc.code,
        ) from exc
    except urllib.error.URLError as exc:
        sanitized_reason = _sanitize_error(str(exc.reason), api_key)
        raise ElevenLabsAPIError(
            f"Failed to connect to ElevenLabs service: {sanitized_reason}",
            status_code=502,
        ) from exc
    except TimeoutError as exc:
        raise ElevenLabsAPIError(
            f"ElevenLabs request timed out after {timeout_seconds} seconds.",
            status_code=504,
        ) from exc
    except Exception as exc:
        sanitized = _sanitize_error(str(exc), api_key)
        raise ElevenLabsAPIError(
            f"Unexpected error communicating with ElevenLabs: {sanitized}",
            status_code=500,
        ) from exc
