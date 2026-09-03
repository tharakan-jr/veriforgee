# Architecture

## Core flow

```text
                ┌────────────────────┐
                │      Web UI        │
                │ Code + Context     │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │    Review API      │
                └─────────┬──────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       ┌───────────────┐       ┌───────────────┐
       │ LLM Analysis  │       │ Rule / Ground │
       │               │       │ Truth Layer   │
       └───────┬───────┘       └───────┬───────┘
               └───────────┬───────────┘
                           ▼
                 ┌───────────────────┐
                 │ Review + Evidence │
                 │ + Fix + Verify    │
                 └─────────┬─────────┘
                           │
                           ▼
                    Optional Voice
                      (ElevenLabs)
```

## Finding schema

Every finding should contain:

- `severity`
- `title`
- `location`
- `explanation`
- `impact`
- `evidence`
- `fix`
- `verification`
- `confidence`

The product should distinguish model reasoning from authoritative evidence. Do not present an LLM statement as official guidance.

## Voice Explanation Service (ElevenLabs)

The ElevenLabs voice feature provides spoken, beginner-friendly explanations of review findings to improve accessibility and comprehension.

### Design Principles

1. **Strictly Optional**: If `ELEVENLABS_API_KEY` is omitted, the entire VeriForge review workflow runs without interruption.
2. **Backend Proxy & Zero Frontend Key Exposure**: Browser clients never receive or hold the `ELEVENLABS_API_KEY`. Requests route through `POST /api/voice/explain`.
3. **Graceful Degradation**: If ElevenLabs experiences upstream downtime, rate limits, or network timeouts, the backend returns clear, sanitized HTTP status codes (`503` / `502`) and the UI notifies the user while leaving the written finding completely visible and functional.
4. **Lightweight & Hackathon-Ready**: Built using Python's standard library (`urllib.request`), adding zero external runtime dependencies.

### Voice API Contracts

#### `GET /api/voice/status`
Returns configuration health for voice synthesis.
```json
{
  "status": "ok",
  "voice": {
    "configured": true,
    "available": true,
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "model_id": "eleven_multilingual_v2"
  },
  "detail": "Voice feature enabled and ready."
}
```

#### `POST /api/voice/explain`
Converts review finding text to speech.

- **Request Body**:
  ```json
  {
    "text": "Your password is directly written inside the source code...",
    "voice_id": "optional-custom-voice-id"
  }
  ```
- **Response**: `audio/mpeg` binary stream (playable directly in HTML5 `<audio>` player).
- **Fallback Status Codes**:
  - `503 Service Unavailable`: `ELEVENLABS_API_KEY` is not configured in `.env`.
  - `502 Bad Gateway`: ElevenLabs API returned an upstream error or network connection failed.
  - `422 Unprocessable Entity`: Request body validation failed (e.g. empty text).
