# Implementation Decisions

## 1. Purpose

This document records the engineering decisions that guide implementation before code exists.

The project is educational. Its goal is not only to build a working product, but to teach how a production-quality RAG system can be designed from first principles.

Every decision must support the approved product and architecture:

- Memory first.
- Evidence before generation.
- Evidence before answers.
- Modular design.
- Explainability over magic.
- Incremental evolution.
- Frameworks support the architecture; they do not define it.

These decisions are technical source-of-truth until explicitly revised by a later ADR.

## 2. Decision Principles

- Prefer tools that make the RAG lifecycle explicit.
- Keep domain boundaries visible in code and tests.
- Avoid frameworks that hide ingestion, chunking, internal retrieval algorithms, evidence, or answer generation behind opaque abstractions.
- Choose boring production tools where they reduce risk.
- Choose AI-native ecosystem tools where they improve learning and implementation quality.
- Defer future-milestone tools until the roadmap requires them.
- Optimize for clarity, traceability, and maintainability over cleverness.

## ADR-001: Programming Language

## Decision

Use Python as the primary programming language.

## Context

This project is fundamentally about AI Engineering: document processing, semantic memory, vector-backed Memory construction, Evidence construction, grounded answer generation, and evidence handling.

The implementation should make those concepts easy to express, test, and teach. The language should support the RAG pipeline as a first-class engineering concern rather than treating AI functionality as an external integration bolted onto a backend.

## Alternatives Considered

### Python

Python has the strongest ecosystem for document processing, machine learning, embeddings, search experimentation, and AI application development. It also has a broad educational footprint in data and AI engineering.

### TypeScript

TypeScript is excellent for typed APIs, frontend-adjacent workflows, and general product backend development. It would be a reasonable choice for a product whose main complexity was web interaction, event-driven backend design, or user-facing application state.

## Rationale

Python best fits this project because the core learning value is the RAG pipeline itself.

The project should teach how source material becomes memory, how memory becomes Evidence, and how Evidence constrains generated answers. Python keeps the implementation close to the AI and document-processing ecosystem where those concepts are most naturally explored.

This is intentionally different from Entrelinhas. Entrelinhas was centered on backend ingestion and deterministic event processing. This project is centered on AI memory architecture.

## Trade-offs

- Python can be less strict than TypeScript without disciplined typing and validation.
- Some web API ergonomics are stronger in TypeScript ecosystems.
- Python dependency ecosystems can drift quickly, especially around AI packages.
- The project must enforce code quality deliberately through validation, type checking, tests, and simple module boundaries.

## ADR-002: Python Version

## Decision

Use Python 3.14 as the project baseline.

Fall back to Python 3.13 only if a concrete compatibility blocker materially affects the project.

## Context

The project is greenfield and will run in a controlled environment using Docker and uv. That means the team can choose a modern Python baseline intentionally instead of optimizing for broad existing-environment compatibility.

Because this project is educational, the baseline should also teach current Python practices. The main risk is package compatibility in AI and document-processing dependencies. That risk should be handled by validating dependencies during setup, not by defaulting to an older version before a real blocker exists.

## Alternatives Considered

### Python 3.13

Python 3.13 is modern, stable, and likely to have excellent package compatibility. It remains the preferred fallback if Python 3.14 blocks required dependencies.

### Python 3.14

Python 3.14 is the preferred baseline for a new project with controlled runtime and dependency management. It provides the longest runway and keeps the project aligned with current Python development.

## Rationale

Python 3.14 is the right default for this project because there is no existing runtime to preserve and no legacy deployment environment to support.

The project should still remain pragmatic. If a required dependency for document processing, database access, testing, or future AI work does not support Python 3.14 in a way that materially affects the roadmap, the project should fall back to Python 3.13 and document the blocker.

## Trade-offs

- Python 3.14 may expose package compatibility issues earlier than Python 3.13.
- Some AI or document-processing packages may lag behind the newest Python version.
- The team must verify dependency compatibility before implementation begins.
- Falling back to Python 3.13 remains acceptable if there is a concrete blocker, not as a default precaution.

## ADR-003: Dependency Management

## Decision

Use uv for dependency management, virtual environment management, and lockfile-based reproducibility.

## Context

The project needs dependency management that is fast, reproducible, easy to teach, and appropriate for a Python AI project.

AI/document dependencies can become heavy. The tooling should make installing, syncing, and locking dependencies predictable.

## Alternatives Considered

### uv

uv provides fast dependency resolution, project management, lockfiles, virtual environment handling, and Python version support in one tool.

### pip

pip is universal and simple, but by itself it does not provide a complete modern project workflow. It needs additional conventions for lockfiles, virtual environments, and dependency groups.

### Poetry

Poetry is mature and widely used, but it adds its own workflow and is slower than uv in common dependency operations.

### PDM

PDM is capable and standards-oriented, but has less momentum than uv for new Python projects.

## Rationale

uv gives the project a fast, reproducible, modern Python workflow without requiring a pile of separate tools.

It is especially useful for an educational project because setup friction matters. Contributors should spend their attention on ingestion, Evidence construction, and evidence design, not environment debugging.

## Trade-offs

- uv is newer than pip and Poetry.
- Some Python developers may be less familiar with it.
- The project should document the chosen workflow clearly once implementation begins.

## ADR-004: API Framework

## Decision

Use FastAPI as the API framework.

## Context

The product needs a simple way to expose import, status, listing, and later query workflows. The API framework should work naturally with typed request/response models and make product contracts explicit.

## Alternatives Considered

### FastAPI

FastAPI is Python-native, type-hint driven, Pydantic-compatible, production-oriented, and easy to understand.

### Flask

Flask is minimal and flexible, but requires more manual work for validation, request schemas, response schemas, and API documentation.

### Django

Django is mature and productive for large web applications, but it brings more application framework than this MVP needs.

### Litestar

Litestar is powerful and well-designed, but has less mindshare for educational RAG examples than FastAPI.

## Rationale

FastAPI provides the right amount of structure without taking over the architecture.

It supports the product's need for explicit contracts while keeping the RAG modules independent. It is a good teaching tool because request validation, response models, and route behavior can be read directly.

## Trade-offs

- FastAPI can encourage putting business logic too close to route handlers if discipline is weak.
- It is not a full application framework, so project boundaries must be designed intentionally.
- The project must keep API concerns separate from ingestion, memory, Evidence construction, and answer-generation modules.

## ADR-005: Validation Layer

## Decision

Use Pydantic v2 for validation and serialization boundaries.

## Context

The system will accept user-provided materials and metadata, track lifecycle states, and later move structured data between ingestion, Evidence construction, and generation modules.

Validation must be explicit because silent coercion or unclear input shape would undermine traceability.

## Alternatives Considered

### Pydantic

Pydantic provides type-hint based validation, structured models, clear serialization, and natural integration with FastAPI.

### dataclasses

Dataclasses are lightweight and standard library based, but do not provide enough validation behavior on their own.

### Alternatives

Other validation libraries can be stricter or more specialized, but they would add ecosystem distance from FastAPI and the broader Python AI stack.

## Rationale

Pydantic v2 gives the project explicit boundaries without excessive boilerplate.

It is appropriate for API contracts, command/input models, configuration, and cross-module DTOs. It should not replace persistence modeling or hide domain behavior.

## Trade-offs

- Pydantic models can be overused as generic data bags.
- Mixing validation models with persistence models can blur architectural boundaries.
- The project must keep validation models separate from storage models when those concepts differ.

## ADR-006: Persistence Layer

## Decision

Use SQLAlchemy 2.x as the persistence layer.

## Context

The system needs durable source records, import lifecycle states, metadata, and later chunks, Memory records, Evidence traces, and evidence references.

Persistence must remain explicit and flexible as the product evolves through the roadmap.

## Alternatives Considered

### SQLAlchemy

SQLAlchemy is the mature Python ORM and SQL toolkit. It supports explicit modeling, flexible queries, and strong integration with Alembic.

### SQLModel

SQLModel combines Pydantic and SQLAlchemy into a simpler model layer. It reduces duplication and can be very productive for small FastAPI applications.

## Rationale

SQLAlchemy is preferred because this project benefits from explicit separation between validation, domain concepts, and persistence.

SQLModel is appealing, but its convenience can blur boundaries. This project should teach how API contracts, domain concepts, and storage models relate without pretending they are always the same thing.

## Trade-offs

- SQLAlchemy has more ceremony than SQLModel.
- Developers must maintain separate Pydantic and persistence models where needed.
- The project must avoid overengineering repositories or abstractions too early.

## ADR-007: Migration Strategy

## Decision

Use Alembic for database migrations.

## Context

The schema will evolve as the roadmap moves from imports to extracted text, chunks, Memory records, Evidence traces, and answers.

Schema changes should be intentional, reviewable, and reversible where practical.

## Alternatives Considered

### Alembic

Alembic is the standard migration tool for SQLAlchemy-based projects.

### Manual SQL migration scripts

Manual scripts are transparent and can be appropriate, but require more discipline around ordering, metadata, and environment integration.

### ORM-driven auto-create

Creating tables directly from models is useful for quick prototypes, but it hides schema evolution and is not appropriate as the project's source of truth.

## Rationale

Alembic gives the project a production-shaped migration path while staying aligned with SQLAlchemy.

It supports the educational goal because schema evolution becomes explicit: each milestone can introduce only the persistence concepts it actually needs.

## Trade-offs

- Alembic adds setup and migration workflow overhead.
- Autogenerated migrations still require human review.
- The team must avoid using migrations as a dumping ground for unrelated schema changes.

## ADR-008: Relational Database

## Decision

Use PostgreSQL as the primary relational database.

## Context

The system needs durable source metadata, lifecycle states, and later memory metadata that remains tightly connected to Evidence.

The database should support the MVP and future vector search direction without forcing a later migration from a demo-only store.

## Alternatives Considered

### PostgreSQL

PostgreSQL is production-proven, expressive, and supports the future pgvector strategy.

### SQLite

SQLite is excellent for local development, small tools, and simple demos. It has low operational overhead and is easy to start with.

## Rationale

PostgreSQL is the better foundation for a production-quality educational RAG system.

The project is about traceable memory. Keeping source records, status, chunks, Memory records, Evidence metadata, and future vectors in one coherent data layer supports the architecture and reduces synchronization complexity.

## Trade-offs

- PostgreSQL is heavier than SQLite for local setup.
- Tests and local development require more environment management.
- For the earliest milestone, PostgreSQL can feel larger than necessary.

## ADR-009: Vector Storage Strategy

## Decision

Use pgvector as the preferred MVP vector storage strategy when Memory construction is introduced.

Milestone 1 will not use vector storage.

## Context

The approved architecture separates product Memory from vector storage infrastructure, but the implementation should avoid splitting operational storage too early.

The product requires tight traceability between source documents, chunks, Memory records, and Evidence.

## Alternatives Considered

### pgvector

pgvector allows vector search inside PostgreSQL, keeping vectors near source metadata and relational context.

### Dedicated vector databases

Dedicated vector databases can provide specialized vector search capabilities, scaling characteristics, and search features.

## Rationale

pgvector best fits the MVP because it keeps vector-backed Memory close to product metadata.

This supports evidence-first answers. Internal search should not become disconnected from the source truth that Evidence must preserve. A unified data layer is easier to explain, test, and operate for the MVP.

Dedicated vector databases remain a future option if scale or Evidence construction requirements justify them.

## Trade-offs

- Dedicated vector databases may outperform pgvector for some large-scale or specialized workloads.
- pgvector keeps more responsibility inside PostgreSQL.
- The team must still preserve the conceptual boundary between product Memory and vector storage infrastructure even if they share the same database.

## ADR-010: Background Processing

## Decision

Do not introduce background processing in Milestone 1.

When asynchronous processing becomes necessary, prefer Dramatiq as the default background processing direction.

## Context

The architecture expects ingestion to become asynchronous because document extraction, chunking, Memory construction, and future processing can be slow or failure-prone.

Milestone 1 only imports and records source material. It does not extract text or build memory, so adding a background worker now would be premature.

## Alternatives Considered

### Dramatiq

Dramatiq provides a focused background task model with a good balance of simplicity, reliability, and production readiness.

### Celery

Celery is mature and powerful, but it is heavier than this project needs in early milestones.

### RQ

RQ is simple and easy to learn, but less expressive for production workflows as processing needs grow.

## Rationale

Dramatiq is the best future direction because it supports asynchronous processing without making the project feel like a distributed systems tutorial.

The project should introduce it only when the roadmap needs it, likely when document processing becomes meaningfully asynchronous.

## Trade-offs

- Dramatiq is less universally known than Celery.
- Celery has a larger ecosystem and more battle-tested advanced features.
- Deferring background processing means Milestone 1 cannot model the full future ingestion lifecycle yet, which is intentional.

## ADR-011: Document Processing Strategy

## Decision

Separate document extraction from ingestion.

Each document type should have its own extraction strategy behind the Document Processing module.

## Context

The roadmap separates Milestone 1, which imports materials, from Milestone 2, which extracts readable text.

This is not just implementation sequencing. It is an architectural distinction: accepting source material is different from understanding its contents.

## Alternatives Considered

### Separate extraction per document type

Each format is handled by a focused extractor that can report success, partial success, or failure.

### One generic extraction pipeline

A generic pipeline can reduce code paths, but often hides format-specific behavior and failure modes.

### External document intelligence service first

External services may be powerful, but they would obscure the educational value of learning extraction boundaries and failure handling.

## Rationale

Extraction should be explicit because source quality directly affects Evidence quality and answer trust.

PDFs, Markdown, plain text, recruiter conversations, and copied email content do not fail in the same ways. Treating each type deliberately makes errors easier to explain and helps users understand whether missing answers come from missing material, failed extraction, weak Evidence construction, or insufficient evidence.

## Trade-offs

- Format-specific strategies create more code paths.
- The project must avoid duplicating common behavior across extractors.
- Early extraction will be less comprehensive than a large external document-processing platform.

## ADR-012: Embedding Provider

## Decision

Own an internal embedding provider abstraction.

Do not couple core architecture directly to a RAG framework or provider SDK.

## Context

Embeddings are an infrastructure mechanism used to build Memory. They are not a business domain entity in TrampoMemo.

The product cares about turning chunks into searchable Memory while preserving source traceability and processing status.

## Alternatives Considered

### Internal abstraction

The project defines its own boundary for vector generation and can adapt embedding providers behind it.

### Direct provider SDK usage throughout the codebase

Direct usage is simple at first, but spreads provider assumptions across the system.

### RAG framework abstraction

Frameworks can accelerate prototypes, but may hide the relationship between chunks, Memory, vector generation, metadata, internal search, and Evidence.

## Rationale

An internal abstraction keeps the architecture honest.

The project should teach that embedding generation is one infrastructure step in a larger memory pipeline. Provider details should not define the domain model, storage model, or Evidence construction behavior.

The provider generates vectors. The application builds Memory.

## Trade-offs

- An internal abstraction must be designed carefully to avoid becoming a vague wrapper.
- Direct SDK usage may be faster for the first experiment.
- The abstraction should stay minimal until multiple providers or test fakes justify expansion.

## ADR-013: LLM Provider

## Decision

Own an internal LLM provider abstraction.

Avoid coupling core product behavior to LangChain, LlamaIndex, or similar frameworks.

The project owns the concepts. Providers are infrastructure details.

## Context

The approved architecture says answer generation is the last step. The LLM receives assembled context and Evidence after Evidence construction has already happened.

The project should not let an external framework decide how Memory, Evidence construction, prompt assembly, or evidence work.

Memory, Evidence, context assembly, prompt assembly, and answer generation are domain concepts in this product. Retrieval is an internal application mechanism used to construct Evidence from Memory. These concepts must remain independent from any specific LLM vendor, SDK, or orchestration framework.

## Alternatives Considered

### Internal abstraction

The project owns the answer-generation boundary and can adapt providers behind it without changing domain concepts.

### Direct provider SDK usage throughout the codebase

This is simple at first, but makes provider behavior leak into business logic.

### LangChain or LlamaIndex as the core orchestration layer

These frameworks are powerful and useful, but they can hide the exact RAG steps this project is meant to teach.

## Rationale

The product's value is not "use an LLM." The value is memory-first, Evidence-first answering.

An internal abstraction keeps prompt assembly, evidence policy, unsupported-answer behavior, and provider calls separate. The LLM provider receives a constrained request from the product; it does not own Memory, Evidence construction, evidence selection, or answer policy.

This protects the architecture from provider lock-in and framework-shaped design. Frameworks may be evaluated later for narrow tasks, but they should not define the core architecture.

## Trade-offs

- The project must implement some orchestration that frameworks provide out of the box.
- Frameworks can accelerate advanced workflows later.
- The team must avoid rebuilding a general-purpose framework; the abstraction should serve only this product.
- Provider abstractions can become vague if they are designed before concrete product needs exist.

## ADR-014: Testing Strategy

## Decision

Use pytest as the primary testing framework.

Favor behavior-driven tests, integration tests around product flows, and focused unit tests for deterministic logic. Avoid tests that only lock down implementation details.

## Context

The project must be educational and production-quality. Tests should explain behavior and protect architecture.

The most important risks are not only function-level bugs. They include broken import status, lost source identity, failed traceability, unsupported answers that look confident, and Evidence construction behavior that cannot be inspected.

## Alternatives Considered

### pytest

pytest supports readable tests, fixtures, parametrization, and a broad Python testing ecosystem.

### unittest

unittest is standard library based and stable, but more verbose and less ergonomic for behavior-focused testing.

### Heavy end-to-end testing only

End-to-end tests are valuable, but relying only on them makes failures harder to diagnose.

## Rationale

pytest is the best fit because it encourages readable tests that can double as executable product documentation.

Milestone tests should validate product capabilities, not internal mechanics. For example, Milestone 1 tests should prove that supported material can be imported, source identity is preserved, imports can be listed, and failures are visible.

## Trade-offs

- Behavior-focused tests require discipline to avoid vague assertions.
- Integration tests can be slower than isolated unit tests.
- The project must still test deterministic internal logic where it matters.

## ADR-015: Project Structure

## Decision

Organize the future project around product capabilities and architectural module boundaries.

Do not create folders or structure until implementation begins.

## Context

The architecture is modular: Import, Document Processing, Chunking, Memory, Metadata Store, Evidence Construction, Context Assembly, Prompt Assembly, Answer Generation, Evidence, Query Interface, and Status.

The code organization should make those responsibilities visible without turning every conceptual module into premature infrastructure.

## Alternatives Considered

### Feature-oriented organization

Group code around product capabilities and bounded responsibilities.

### Technical-layer organization

Separate files primarily by technical layer, such as routes, models, services, repositories, and schemas.

### Framework-driven organization

Follow whatever structure a framework or tutorial suggests.

## Rationale

Feature-oriented organization better supports the roadmap.

Milestone 1 should focus on imports. Later milestones should add document processing, memory building, Evidence construction, and answering without scattering each feature across many unrelated technical folders.

The structure should make it easy to answer: what does this module own, what does it depend on, and what product behavior does it support?

## Trade-offs

- Feature-oriented organization can still drift if boundaries are not maintained.
- Some shared infrastructure will still be necessary.
- The team must avoid creating abstractions for future milestones before those milestones begin.

## ADR-016: Code Quality

## Decision

Use Ruff for formatting and linting, static typing as a standard practice, pytest for verification, and clear documentation for architectural decisions and non-obvious behavior.

Prefer readable, explicit code over clever code.

## Context

The project is educational and must remain maintainable as it moves from import tracking to RAG behavior.

The code should teach good engineering habits: explicit state, traceable source relationships, clear module boundaries, and honest failure handling.

## Alternatives Considered

### Ruff

Ruff provides fast formatting and linting with low tooling overhead.

### Separate formatting and linting tools

Traditional combinations can work well, but increase configuration and cognitive load.

### Minimal tooling

Minimal tooling reduces setup, but makes consistency depend too much on individual discipline.

## Rationale

Ruff plus static typing gives the project a strong quality baseline without turning tooling into the project.

The standards should reinforce the product philosophy:

- explicit status over hidden state
- clear errors over silent failures
- small modules over tangled flows
- typed boundaries over ambiguous dictionaries
- documentation where behavior affects trust

## Trade-offs

- Static typing takes time and must be applied thoughtfully.
- Strict tooling can slow early experimentation.
- The team must avoid optimizing for tool satisfaction instead of product clarity.

## 3. Final Stack Direction

The approved implementation direction is:

- Python 3.14, with fallback to Python 3.13 only for concrete compatibility blockers.
- uv.
- FastAPI.
- Pydantic v2.
- SQLAlchemy 2.x.
- Alembic.
- PostgreSQL.
- pgvector when Memory construction begins.
- Dramatiq when asynchronous processing becomes necessary.
- pytest.
- Format-specific document extraction beginning in Milestone 2.
- Internal embedding provider abstraction beginning in Milestone 4.
- Internal LLM provider abstraction beginning in Milestone 6.
- Ruff and static typing for code quality.

Milestone 1 must not introduce document extraction, Memory construction, vector storage, background processing, Evidence construction, prompt assembly, answer generation, or LLM integration.

## 4. Final Review

These decisions were reviewed against the approved product requirements, architecture, and roadmap.

### Product Fit

The stack is Python-first because the product is AI Engineering first. It supports document processing, vector-backed Memory construction, Evidence construction, and grounded generation as the core educational value.

### Architecture Fit

The decisions preserve the approved architecture:

- Ingestion is distinct from extraction.
- Extraction is distinct from chunking.
- Chunking is distinct from Memory construction.
- Product Memory remains distinct from vector storage infrastructure.
- Evidence construction happens before generation.
- Evidence remains a first-class product concern.

### Roadmap Fit

The decisions do not pull future milestones into Milestone 1.

Milestone 1 remains limited to importable job search memory: source identity, import status, listing imports, and visible failures.

### Complexity Check

The project intentionally avoids using LangChain, LlamaIndex, dedicated vector databases, Celery, OCR, or multi-provider abstractions before the roadmap requires them.

The goal is not to avoid powerful tools forever. The goal is to introduce tools only when they serve a clearly understood architectural responsibility.

### Educational Check

The chosen direction teaches RAG concepts directly instead of hiding them behind a framework.

Readers should be able to see how source documents become Memory, how Memory becomes Evidence, and how Evidence constrains Answers.
