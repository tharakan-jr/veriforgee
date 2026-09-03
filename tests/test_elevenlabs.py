"""
Unit tests for ElevenLabs integration in VeriForge.
"""

import io
import json
import os
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.responses import Response

from app import elevenlabs
from app.main import VoiceExplainRequest, explain_voice, health, voice_status


class TestElevenLabsService(unittest.TestCase):
    """Test suite for app/elevenlabs.py service functions."""

    def setUp(self):
        # Clear environment variables before each test
        self.original_api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.original_voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
        if "ELEVENLABS_API_KEY" in os.environ:
            del os.environ["ELEVENLABS_API_KEY"]
        if "ELEVENLABS_VOICE_ID" in os.environ:
            del os.environ["ELEVENLABS_VOICE_ID"]

    def tearDown(self):
        # Restore environment variables
        if self.original_api_key is not None:
            os.environ["ELEVENLABS_API_KEY"] = self.original_api_key
        elif "ELEVENLABS_API_KEY" in os.environ:
            del os.environ["ELEVENLABS_API_KEY"]

        if self.original_voice_id is not None:
            os.environ["ELEVENLABS_VOICE_ID"] = self.original_voice_id
        elif "ELEVENLABS_VOICE_ID" in os.environ:
            del os.environ["ELEVENLABS_VOICE_ID"]

    def test_health_endpoint(self):
        """Ensure standard health check remains intact."""
        res = health()
        self.assertEqual(res, {"status": "ok"})

    def test_status_unconfigured(self):
        """Voice status should report configured=False and safe defaults when key is missing."""
        self.assertFalse(elevenlabs.is_configured())
        status = elevenlabs.get_status()
        self.assertFalse(status["configured"])
        self.assertFalse(status["available"])
        self.assertIn("voice_id", status)
        self.assertIn("model_id", status)
        self.assertNotIn("api_key", status)
        self.assertNotIn("ELEVENLABS_API_KEY", status)

    def test_status_configured(self):
        """Voice status should report configured=True without exposing the key."""
        fake_secret = "test-secret-key-12345"
        os.environ["ELEVENLABS_API_KEY"] = fake_secret
        self.assertTrue(elevenlabs.is_configured())
        status = elevenlabs.get_status()
        self.assertTrue(status["configured"])
        self.assertTrue(status["available"])
        # Verify key is never exposed
        self.assertNotIn(fake_secret, str(status))

    def test_synthesize_unconfigured_raises_error(self):
        """Calling synthesize_speech without API key should raise ElevenLabsNotConfiguredError."""
        with self.assertRaises(elevenlabs.ElevenLabsNotConfiguredError) as ctx:
            elevenlabs.synthesize_speech("Hello world")
        self.assertEqual(ctx.exception.status_code, 503)

    def test_synthesize_empty_text_raises_value_error(self):
        """Empty text should raise ValueError."""
        os.environ["ELEVENLABS_API_KEY"] = "fake-key"
        with self.assertRaises(ValueError):
            elevenlabs.synthesize_speech("   ")

    @patch("urllib.request.urlopen")
    def test_synthesize_speech_success(self, mock_urlopen):
        """Mock successful response from ElevenLabs API."""
        fake_secret = "sk-test-secret-key-999"
        os.environ["ELEVENLABS_API_KEY"] = fake_secret

        mock_response = MagicMock()
        mock_response.read.return_value = b"\xff\xfb\x90\x00fake-mp3-audio-stream"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        audio = elevenlabs.synthesize_speech("Your password is hardcoded.")
        self.assertEqual(audio, b"\xff\xfb\x90\x00fake-mp3-audio-stream")
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_synthesize_speech_api_error_redacts_credentials(self, mock_urlopen):
        """Mock ElevenLabs API error response and verify credentials are redacted."""
        fake_secret = "sk-secret-key-elevenlabs"
        os.environ["ELEVENLABS_API_KEY"] = fake_secret

        error_body = json.dumps({"detail": {"message": "Invalid API key provided"}})
        http_error = urllib.error.HTTPError(
            url="https://api.elevenlabs.io/v1/text-to-speech/test",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(error_body.encode("utf-8")),
        )
        mock_urlopen.side_effect = http_error

        with self.assertRaises(elevenlabs.ElevenLabsAPIError) as ctx:
            elevenlabs.synthesize_speech("Sample text")

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Invalid API key", str(ctx.exception))
        self.assertNotIn(fake_secret, str(ctx.exception))


class TestVoiceEndpoints(unittest.TestCase):
    """Test suite for FastAPI route handlers."""

    def setUp(self):
        if "ELEVENLABS_API_KEY" in os.environ:
            del os.environ["ELEVENLABS_API_KEY"]

    def test_voice_status_route_disabled(self):
        """GET /api/voice/status when disabled."""
        resp = voice_status()
        self.assertEqual(resp["status"], "ok")
        self.assertFalse(resp["voice"]["configured"])
        self.assertIn("disabled", resp["detail"])

    def test_explain_voice_unconfigured_returns_503(self):
        """POST /api/voice/explain when API key is unset returns 503 Service Unavailable."""
        req = VoiceExplainRequest(text="Why this matters: your password is plain text.")
        with self.assertRaises(HTTPException) as ctx:
            explain_voice(req)
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertFalse(ctx.exception.detail["available"])
        self.assertIn("ELEVENLABS_API_KEY", ctx.exception.detail["message"])

    @patch("app.elevenlabs.synthesize_speech")
    def test_explain_voice_success(self, mock_synthesize):
        """POST /api/voice/explain when configured returns MP3 Response."""
        os.environ["ELEVENLABS_API_KEY"] = "mock-valid-key"
        mock_synthesize.return_value = b"mp3-binary-content"

        req = VoiceExplainRequest(text="Explain this vulnerability")
        resp = explain_voice(req)

        self.assertIsInstance(resp, Response)
        self.assertEqual(resp.media_type, "audio/mpeg")
        self.assertEqual(resp.body, b"mp3-binary-content")


if __name__ == "__main__":
    unittest.main()
