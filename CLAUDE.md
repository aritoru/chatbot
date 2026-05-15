# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AD&DHelp Conversational Agent** — an AI-powered chatbot that conducts short interviews with customers who have questions about Advanced Dungeons & Dragons (AD&D) RPGs. The agent collects: game system, problem category, problem description, and urgency level — then stores structured Intakes with a system-generated Issue Reference Number.

See `CONTEXT.md` for the canonical domain language (Customer, Agent, Interview, Intake, Knowledge Query, etc.). Use those terms precisely when reading or writing code.

## Repository Layout

```
back/              # Python backend (FastAPI)
  models/          # Pydantic data models
    interview.py   # GameSystem, UrgencyLevel, InterviewFields, Session, etc.
  services/
    agent.py       # Claude API integration + interview state machine
    storage.py     # JSON file Intake persistence
  routers/
    chat.py        # POST /sessions, POST /sessions/{id}/messages, DELETE /sessions/{id}
    intakes.py     # GET /intakes, GET /intakes/{irn}
  main.py          # FastAPI app + CORS
  requirements.txt
  .env.example
front/             # React + Vite frontend
  src/
    components/Chat.tsx  # Chat UI
    services/api.ts      # fetch wrappers
    types.ts             # TypeScript types
    App.tsx, main.tsx
  package.json
  vite.config.ts
docs/
  README.md        # Project requirements
  adr/             # Architecture Decision Records
    0001-server-side-sessions.md
    0002-claude-as-llm.md
openspec/          # Spec-driven design artifacts
CONTEXT.md         # Domain language glossary
```

## Technical Decisions

- **Backend**: FastAPI + Uvicorn, Python
- **Frontend**: React 18 + Vite, TypeScript
- **LLM**: Claude `claude-sonnet-4-6` via Anthropic Python SDK — tool_use for field extraction (see ADR 0002)
- **Session storage**: Server-side in-memory dict keyed by UUID (see ADR 0001) — `_sessions` in `routers/chat.py`; entry is deleted the moment `confirm_intake` runs, so subsequent calls to the same session_id return 404
- **Intake storage**: Flat JSON files in `back/data/intakes/`, named by Issue Reference Number
- **Issue Reference Number format**: `IRN-XXXXXXXX` (8 uppercase hex chars from `uuid4().hex[:8]`, see `services/storage.py`)
- **CORS**: `main.py` allows `http://localhost:5173` only (matches Vite dev server)
- **Config**: `python-dotenv` from `.env`; requires `ANTHROPIC_API_KEY`

## Domain Model (`back/models/interview.py`)

- `GameSystem` — enum: AD&D 1e, AD&D 2e, D&D 3/3.5, D&D 4e, D&D 5e, Other
- `UrgencyLevel` — enum: Low, Medium, High
- `InterviewStatus` — enum: in_progress, awaiting_confirmation, completed
- `InterviewFields` — four collected fields; `.is_complete()` checks all are set
- `Session` — in-memory: holds `InterviewFields`, `InterviewStatus`, transcript, raw Claude messages

## Agent Architecture (`back/services/agent.py`)

The system prompt is **regenerated on every request** with the current Interview State injected, so Claude always knows which fields are collected. Claude uses two tools:
- `extract_field(field_name, field_value)` — called whenever Claude extracts a valid field value
- `confirm_intake()` — called when the customer confirms the summary

The backend runs a tool loop: send → handle tool calls → send tool results → repeat until `end_turn`. The opening greeting is generated separately (`get_opening_message`) with a one-shot prompt suffix and no tools — it just seeds `claude_messages` with a `[BEGIN INTERVIEW]` user turn plus the assistant greeting.

**HTTP API:**
- `POST /sessions` → creates session, returns `{session_id, message}` (opening greeting)
- `POST /sessions/{id}/messages` → sends customer turn, returns `{message, status, intake?}` (intake non-null only on confirmation)
- `DELETE /sessions/{id}` → explicit session close
- `GET /intakes` → list all intakes (summary fields only)
- `GET /intakes/{irn}` → full intake including transcript

## Development Setup

**Backend:**
```bash
cd back
cp .env.example .env    # add your ANTHROPIC_API_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Frontend:**
```bash
cd front
npm install
npm run dev
# UI available at http://localhost:5173
```

## OpenSpec Workflow

Changes are proposed in `openspec/changes/`, archived after application, specs in `openspec/specs/`. Use `/openspec-propose`, `/openspec-explore`, `/openspec-apply-change` skills.
