# Architecture

## Overview

Decision OS is split into two independently runnable services:

- **`backend/`** — a FastAPI service that owns all persistence, business
  logic, and LLM integration. It exposes a versioned REST API under
  `/api/v1`.
- **`frontend/`** — a Streamlit app that talks to the backend over HTTP
  and renders the user-facing experience.

They communicate only over the network (HTTP/JSON), so either can be
redeployed, scaled, or replaced independently. The `docker-compose.yml`
at the repo root wires both up alongside a Postgres database for local
development.

```
┌─────────────┐      HTTP/JSON      ┌──────────────┐      SQL      ┌────────────┐
│  Streamlit   │  ───────────────►  │   FastAPI     │  ─────────►  │ PostgreSQL │
│  frontend    │  ◄───────────────  │   backend     │  ◄─────────  │            │
└─────────────┘                     └──────┬───────┘               └────────────┘
                                            │
                                            │ prompt / completion
                                            ▼
                                   ┌──────────────────┐
                                   │  LLM provider     │
                                   │ (OpenAI/Gemini/   │
                                   │  Groq — pluggable)│
                                   └──────────────────┘
```

## Backend layout

| Layer        | Responsibility                                                            |
|--------------|----------------------------------------------------------------------------|
| `api/`       | HTTP routing only — request/response wiring, no business logic            |
| `schemas/`   | Pydantic models defining the shape of API requests/responses               |
| `services/`  | Business logic: scoring, learning, decision orchestration, explanations    |
| `models/`    | SQLAlchemy ORM models — the persistence shape                              |
| `ai/`        | LLM provider abstraction + prompt templates, isolated from business logic |
| `core/`      | Cross-cutting config, logging, security                                    |
| `database/`  | Engine/session setup and Alembic migrations                                |
| `utils/`     | Small stateless helpers (e.g. weight normalization) shared across services |

Routes depend on services; services depend on models and the `ai/` layer.
Nothing in `services/` or `models/` imports from `api/`, which keeps the
business logic testable without spinning up the HTTP layer (see
`backend/tests/test_scoring.py` and `test_preferences.py`, which test
`services/` and `utils/` directly).

## Request flow: evaluating a decision

1. Client calls `POST /api/v1/decisions` with a title and candidate
   options → `decision_service.create_decision` persists a `Decision`
   row plus one `Option` row per candidate.
2. Client calls `POST /api/v1/decisions/{id}/evaluate` →
   `decision_service.evaluate_decision`:
   - `scoring_service.score_options` pulls the user's normalized
     preference weights and computes a weighted score per option.
   - `explanation_service.generate_explanation` builds a prompt from the
     ranked options and calls the configured `ai.llm_service.LLMService`
     to produce a natural-language explanation, with a deterministic
     fallback if the LLM call fails.
   - The top-ranked option and explanation are persisted back onto the
     `Decision` row.
3. Client later calls `POST /api/v1/feedback` with a satisfaction
   rating → `learning_service.apply_feedback` nudges the user's
   preference weights up or down, so future evaluations reflect what
   actually worked out.

## Why a pluggable LLM layer

`ai/llm_service.py` picks a provider (`openai`, `gemini`, or `groq`) by
name from `core/config.py`. Each provider module in `ai/providers/`
exposes the same `complete(prompt: str) -> str` signature, so swapping
providers — or adding a new one — never touches `services/` or `api/`.

## Frontend

The Streamlit app is deliberately thin: each page under `frontend/pages/`
maps to one part of the user journey (profile/preferences, creating a
decision, history, insights) and is expected to call the backend API
directly via `requests`. No business logic should live in the frontend —
if a page needs to compute something, that computation belongs in a
backend service instead.

## Extension points

- **New preference categories**: no schema change needed — `category`
  is a free-text string, and `scoring_service.score_option` picks up
  any category present in both an option's `attributes` and the user's
  weights.
- **New LLM provider**: add a module to `ai/providers/` with a
  `complete()` function and register it in `_PROVIDERS` in
  `ai/llm_service.py`.
- **New data store**: swap `DATABASE_URL` — the app only depends on
  SQLAlchemy's engine abstraction, not Postgres specifically.
