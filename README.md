# TrampoMemo

TrampoMemo is an AI-powered memory for job search materials.

It helps a user import resumes, job descriptions, company notes, recruiter conversations, interview feedback, personal notes, and similar materials, then ask grounded questions over that material.

The core domain flow is:

```text
Source -> SourceContent -> Chunk -> Memory -> Evidence -> Answer
```

TrampoMemo is not a chatbot-first project. It is a memory system. The application builds Memory, constructs Evidence, and only then asks a language provider to generate an Answer from that Evidence.

## MVP Capabilities

- Create Sources from direct text or supported files.
- Preserve Source identity and import status.
- Extract reviewable SourceContent.
- Create reviewable Chunks.
- Build Memory from Chunks.
- Construct Evidence from Memory for a user question.
- Construct Answers from Evidence.
- Review Sources, SourceContent, Chunks, Memory, Evidence, and Answers through the API.

## Architectural Rules

- Answers are built from Evidence, never directly from Memory.
- Evidence is question-specific.
- Memory exists independently of questions.
- Embedding providers generate vectors as infrastructure.
- LLM providers generate text from prompts only.
- Providers do not own Source, Chunk, Memory, Evidence, or Answer.
- LangChain, LlamaIndex, external AI providers, chat history, agents, and streaming are intentionally out of scope for this MVP.

## Requirements

- Python 3.14
- uv
- PostgreSQL for production-shaped local runs

Tests use an in-memory database and do not require API keys.

## Setup

```bash
uv sync
cp .env.example .env
```

Update `.env` if your local PostgreSQL connection differs from the example.

## Database Migrations

```bash
uv run alembic upgrade head
```

## Run The API

```bash
uv run uvicorn trampomemo.main:app --reload
```

## Quality Gate

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Main API Flow

1. `POST /sources`
2. `POST /sources/{source_id}/content`
3. `POST /sources/{source_id}/content/chunks`
4. `POST /sources/{source_id}/content/chunks/memory`
5. `POST /evidence`
6. `POST /answers`

Review endpoints are also available:

- `GET /sources`
- `GET /sources/{source_id}/content`
- `GET /sources/{source_id}/content/chunks`
- `GET /sources/{source_id}/content/chunks/memory`
- `GET /evidence`
- `GET /answers`

## Current Providers

The MVP uses deterministic local providers for Memory construction and Answer construction.

These providers are development and testing tools. They make the architecture fully testable without API keys, but they are not semantic production AI models.
