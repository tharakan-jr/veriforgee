"""
VeriForge FastAPI Application.

Core review workflow with optional ElevenLabs voice explanation feature.
"""

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from app import elevenlabs

app = FastAPI(
    title="VeriForge",
    description="AI-assisted review, explanation, grounding, and verification for non-expert builders.",
    version="0.1.0",
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


@app.get("/", response_class=HTMLResponse)
def home():
    """
    Landing page showcasing VeriForge core review workflow with the
    optional ElevenLabs voice explanation integration.
    """
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VeriForge - AI-Assisted Code Review & Voice Explanation</title>
  <style>
    :root {
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --text: #0f172a;
      --text-muted: #475569;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --danger-bg: #fee2e2;
      --danger-text: #b91c1c;
      --code-bg: #f1f5f9;
      --info-bg: #f0f9ff;
      --info-border: #bae6fd;
      --info-text: #0369a1;
      --warn-bg: #fef3c7;
      --warn-border: #fde68a;
      --warn-text: #92400e;
    }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 860px;
      margin: 40px auto;
      padding: 0 20px 60px;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }
    header {
      margin-bottom: 28px;
    }
    h1 {
      margin: 0 0 6px 0;
      font-size: 2.2rem;
      letter-spacing: -0.02em;
    }
    .subtitle {
      margin: 0;
      color: var(--text-muted);
      font-size: 1.05rem;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      margin-bottom: 24px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--danger-bg);
      color: var(--danger-text);
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .finding-title {
      font-size: 1.45rem;
      margin: 14px 0 10px;
      color: var(--text);
    }
    .code-box {
      background: var(--code-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.95rem;
      color: #0f172a;
      overflow-x: auto;
      margin: 12px 0 16px;
    }
    .section-title {
      font-size: 1.05rem;
      font-weight: 600;
      margin: 16px 0 6px;
      color: var(--text);
    }
    .explanation-text {
      color: var(--text-muted);
      font-size: 1rem;
      line-height: 1.6;
      margin: 0 0 18px;
    }
    .voice-action-area {
      border-top: 1px solid var(--border);
      padding-top: 18px;
      margin-top: 18px;
    }
    .btn-voice {
      background: var(--primary);
      color: #ffffff;
      border: none;
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: background 0.15s ease, transform 0.1s ease;
    }
    .btn-voice:hover:not(:disabled) {
      background: var(--primary-hover);
    }
    .btn-voice:disabled {
      opacity: 0.65;
      cursor: not-allowed;
    }
    .status-msg {
      margin-top: 12px;
      font-size: 0.9rem;
      min-height: 20px;
    }
    .alert-banner {
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 0.9rem;
      line-height: 1.5;
      margin-top: 12px;
    }
    .alert-warn {
      background: var(--warn-bg);
      border: 1px solid var(--warn-border);
      color: var(--warn-text);
    }
    .alert-info {
      background: var(--info-bg);
      border: 1px solid var(--info-border);
      color: var(--info-text);
    }
    audio {
      width: 100%;
      margin-top: 12px;
      border-radius: 8px;
    }
    footer {
      font-size: 0.85rem;
      color: var(--text-muted);
      text-align: center;
      margin-top: 40px;
    }
  </style>
</head>
<body>
  <header>
    <h1>VeriForge</h1>
    <p class="subtitle">Paste AI-generated code → Review → Explain → Ground → Fix → Verify.</p>
  </header>

  <main>
    <div class="card" id="finding-card">
      <div>
        <span class="badge">🔴 Critical</span>
      </div>

      <h2 class="finding-title">Hardcoded Database Password</h2>

      <div class="code-box">
        <code>DB_PASSWORD = "admin123"</code>
      </div>

      <div class="section-title">Why this matters:</div>
      <p id="finding-explanation" class="explanation-text">
        Your password is directly written inside the source code. Anyone with access to this repository or build artifact can see your database credentials and compromise the entire system. Passwords and secrets should always be loaded through secure environment variables or a secrets manager, never hardcoded in plaintext.
      </p>

      <div class="voice-action-area">
        <button id="voice-btn" class="btn-voice" onclick="handleExplainVoice()">
          <span>🔊</span> <span>Explain with Voice</span>
        </button>

        <div id="voice-status-container"></div>
        <audio id="audio-player" controls style="display: none;"></audio>
      </div>
    </div>
  </main>

  <footer>
    VeriForge &bull; Microsoft Innovation Club Hackathon &bull; Voice powered optionally by ElevenLabs
  </footer>

  <script>
    async function handleExplainVoice() {
      const btn = document.getElementById('voice-btn');
      const statusContainer = document.getElementById('voice-status-container');
      const audioPlayer = document.getElementById('audio-player');
      const explanationText = document.getElementById('finding-explanation').innerText.trim();

      btn.disabled = true;
      btn.innerHTML = '<span>⏳</span> <span>Generating spoken audio...</span>';
      statusContainer.innerHTML = '<div class="status-msg" style="color: var(--text-muted);">Requesting voice synthesis from ElevenLabs via backend proxy...</div>';
      audioPlayer.style.display = 'none';

      try {
        const response = await fetch('/api/voice/explain', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: explanationText })
        });

        if (response.ok) {
          const blob = await response.blob();
          const audioUrl = URL.createObjectURL(blob);
          audioPlayer.src = audioUrl;
          audioPlayer.style.display = 'block';
          audioPlayer.play().catch(e => {
            // Autoplay may be restricted by browser policy; user can still press play
            console.log("Autoplay prevented:", e);
          });
          statusContainer.innerHTML = '<div class="alert-banner alert-info">✅ Voice explanation ready. Listen using the audio player below.</div>';
        } else {
          let errorDetail = "Voice explanation could not be generated.";
          try {
            const errData = await response.json();
            if (errData && errData.detail && errData.detail.message) {
              errorDetail = errData.detail.message;
            } else if (errData && errData.detail) {
              errorDetail = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
            }
          } catch (e) {
            errorDetail = `Server returned status ${response.status}.`;
          }

          statusContainer.innerHTML = `
            <div class="alert-banner alert-warn">
              <strong>Voice explanation unavailable:</strong> ${errorDetail}
              <div style="margin-top: 4px; font-size: 0.85rem; color: #78350f;">
                Note: VeriForge text review findings remain fully accessible above.
              </div>
            </div>
          `;
        }
      } catch (err) {
        statusContainer.innerHTML = `
          <div class="alert-banner alert-warn">
            <strong>Network error:</strong> Unable to reach VeriForge backend audio endpoint.
            <div style="margin-top: 4px; font-size: 0.85rem;">The written review finding above is unaffected.</div>
          </div>
        `;
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🔊</span> <span>Explain with Voice</span>';
      }
    }
  </script>
</body>
</html>
"""
