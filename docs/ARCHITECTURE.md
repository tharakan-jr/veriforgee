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
