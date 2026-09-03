# VeriForge

> **AI-assisted review, explanation, grounding, and verification for non-expert builders.**

Hackathon project for **Microsoft Innovation Club, VIT Chennai** — Developer Tools & Human-AI Interaction.

## Problem

AI has made creating software easier, but judging whether generated output is correct, safe, maintainable, and grounded still requires expertise. The official problem statement calls for expert judgement in plain language, grounded in project context, official documentation, applicable standards, or verified checks, at the moment the artefact is created.

## Our MVP

**Paste code → Review → Explain → Ground → Fix → Verify**

1. User submits AI-generated code.
2. VeriForge identifies high-impact issues.
3. Each finding is explained in beginner-friendly language.
4. Findings are grounded in authoritative guidance or verified checks.
5. The user gets a concrete fix.
6. A verification question/check confirms understanding.

## Sponsor alignment

- **Microsoft Innovation Club** — primary problem statement / hackathon context.
- **ElevenLabs** — optional voice layer for spoken explanations and accessibility.
- **Code Crafters** — developer tooling / implementation ecosystem.

## Repository structure

```text
.
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO.md
│   └── DATASET.md
├── .github/
│   ├── ISSUE_TEMPLATE/bug_report.md
│   └── pull_request_template.md
├── app/
│   ├── main.py
│   └── elevenlabs.py
├── tests/
│   └── test_elevenlabs.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Quick start

### Local Development

1. Create and configure environment:
   ```bash
   copy .env.example .env   # On Windows
   # or: cp .env.example .env (Linux/macOS)
   ```
2. Run backend dev server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Open `http://localhost:8000` in your browser.

### Docker

```bash
docker compose up --build
```

### Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## ElevenLabs Voice Integration

VeriForge includes an optional voice explanation layer powered by ElevenLabs Text-to-Speech to make security and code findings accessible through natural speech.

### 1. Configuration

Copy `.env.example` to `.env` and add your API key:

```bash
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

Optional settings:
```bash
# Custom Voice ID (defaults to Rachel: 21m00Tcm4TlvDq8ikWAM)
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Custom Model (defaults to eleven_multilingual_v2)
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

> **Security & Graceful Fallback**:
> - Never commit `.env` to Git. `.gitignore` is preconfigured to prevent this.
> - ElevenLabs is **strictly optional**. If `ELEVENLABS_API_KEY` is not provided, VeriForge continues operating normally; findings remain 100% visible and interactive.
> - The API key is securely handled by the backend proxy and is **never** exposed to the browser.

### 2. Example API Requests

#### Check Voice Health / Status:
```bash
curl -X GET http://localhost:8000/api/voice/status
```
Response:
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

#### Generate Spoken Finding Audio:
```bash
curl -X POST http://localhost:8000/api/voice/explain \
  -H "Content-Type: application/json" \
  -d '{"text": "Your database password is directly written inside the source code. Passwords should always be loaded through secure environment variables."}' \
  --output explanation.mp3
```

## Environment variables

Copy `.env.example` to `.env` and add only the keys your implementation actually uses. **Never commit `.env`.**

## Team rules for the 24-hour hackathon

- `main` must always be demoable.
- One feature = one branch.
- Commit frequently.
- No API keys, tokens, passwords, or personal credentials in Git.
- Prefer working MVPs over unfinished features.
- Every major feature needs a short README/docs update.
- Keep the final demo path under 2 minutes from landing page to result.

## Current status

- [ ] UI
- [ ] Review API
- [ ] Structured finding schema
- [ ] Grounding / evidence layer
- [ ] Verification flow
- [x] ElevenLabs voice demo
- [ ] Docker smoke test
- [ ] Final demo script
