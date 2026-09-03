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
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Quick start

### Docker

```bash
docker compose up --build
```

### Local Git workflow

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd veriforge
git checkout -b feature/<short-name>
```

Make small commits and open a PR before merging into `main`.

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
- [ ] ElevenLabs voice demo
- [ ] Docker smoke test
- [ ] Final demo script
