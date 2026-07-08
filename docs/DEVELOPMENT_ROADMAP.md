# Development Roadmap: AI-Powered Job Search Memory

## 1. Roadmap Purpose

This roadmap describes how the product will be built incrementally from approved requirements and architecture.

The MVP must prove one complete loop:

```text
Import knowledge
        |
        v
Build semantic memory
        |
        v
Ask a question
        |
        v
Construct Evidence
        |
        v
Generate a grounded answer
```

Each milestone delivers a product capability that can be demonstrated and reviewed. The roadmap avoids isolated technical milestones such as "add embeddings" or "add answer generation." Those capabilities matter, but they only create product value when they help users ingest, construct Evidence, verify, and act on their own job search knowledge.

## 2. Roadmap Principles

- Follow the approved product requirements and architecture.
- Build Knowledge Ingestion before Evidence and Answering.
- Keep evidence visible from the beginning.
- Deliver useful product behavior after every milestone.
- Keep the MVP focused on a single-user job search memory.
- Avoid scope creep into accounts, dashboards, agents, collaboration, deployment, or advanced retrieval features.
- Preserve the principle that the system constructs Evidence from Memory before generating answers.

## 3. Milestone Overview

| Milestone | Product Capability | Primary Flow |
| --- | --- | --- |
| 1 | The system can accept and track job search material | Knowledge Ingestion |
| 2 | The system can turn imported material into reviewable text | Knowledge Ingestion |
| 3 | The system can prepare source material as reviewable chunks | Knowledge Ingestion |
| 4 | The system can build Memory from chunks | Knowledge Ingestion |
| 5 | The system can construct Evidence from Memory for a question | Evidence and Answering |
| 6 | The system can answer questions using Evidence | Evidence and Answering |

## 4. Milestone 1: Importable Job Search Memory

### Goal

The system can accept user-provided job search materials and track their import status.

### Why This Milestone Exists

Before the product can search knowledge, it must reliably know what material exists. This milestone establishes the user's job search collection as the root of the product memory.

The product is not useful yet as an intelligent memory, but it becomes useful as a controlled place where job search materials can be collected, listed, and reviewed by source.

### Product Capabilities Delivered

- Users can import supported job search materials.
- Imported materials retain source identity, such as title, content type, origin, and date when available.
- Users can see which materials have been imported.
- Each import has a visible status.
- Failed or unsupported imports are reported clearly.
- Imported materials are not mixed with unrelated imports.

### Acceptance Criteria

- A user can import representative MVP materials:
  - PDF documents.
  - Markdown files.
  - Plain text files.
  - Job descriptions.
  - Company information.
  - Recruiter conversations.
  - Interview feedback.
  - Personal notes.
  - Copied or exported email content.
- The system shows a list of imported materials.
- Each imported item displays enough source information for the user to recognize it.
- The system distinguishes successful imports from failed or unsupported imports.
- The user can confirm that source identity is preserved before deeper processing exists.

### Explicitly Out of Scope

- Search.
- Semantic memory.
- Natural language questions.
- Grounded answers.
- Source comparison.
- Automatic classification of companies, recruiters, or roles.
- External account synchronization.
- User accounts or authentication.

## 5. Milestone 2: Reviewable Knowledge Extraction

### Goal

The system can extract readable text from imported materials and make that text reviewable.

### Why This Milestone Exists

The product cannot build trustworthy memory from opaque files. Users need confidence that the system can read their material before it tries to construct Evidence or answer from it.

This milestone creates the first bridge between documents and knowledge. It also makes failures visible early, which protects later answers from silent gaps.

### Product Capabilities Delivered

- Imported materials can be processed into readable text.
- Users can review extracted text or relevant extracted sections.
- Processing status is visible:
  - Processing.
  - Ready for memory building.
  - Partially processed.
  - Failed.
- Partial extraction is treated honestly instead of being hidden.
- Empty or unreadable materials are identified.
- Source identity remains connected to extracted text.

### Acceptance Criteria

- A user can import several representative materials and see which ones were successfully converted into readable text.
- The user can inspect extracted text for at least one imported source.
- The system clearly identifies materials that could not be processed.
- The system distinguishes failed extraction from successful import.
- The user can understand whether missing future answers may be caused by unreadable source material.

### Explicitly Out of Scope

- Semantic search.
- Answer generation.
- Automatic summarization.
- OCR.
- Advanced document cleanup.
- Manual correction workflows.
- Analytics dashboards.
- Multi-format expansion beyond the approved MVP inputs.

## 6. Milestone 3: Reviewable Memory Units

### Goal

The system can transform extracted material into reviewable chunks while preserving source traceability.

### Why This Milestone Exists

This milestone turns a collection of readable documents into focused memory units.

The user may not yet ask full natural language questions, but the system now has the chunk structure required to later build Memory from job descriptions, recruiter notes, interview feedback, and personal notes.

### Product Capabilities Delivered

- Extracted text is split into meaningful memory units.
- Each memory unit remains linked to its original source.
- Long materials become prepared for Memory construction without losing source context.
- The system can show which sources have reviewable chunks.
- Materials with incomplete preparation remain visible as partially processed.
- The product can explain which sources are ready for Memory construction.

### Acceptance Criteria

- A user can import and process a representative set of job search materials.
- The system can show which sources have reviewable chunks.
- The system preserves the relationship between source material and prepared memory units.
- The system does not treat failed or incomplete material as ready for Memory construction.
- The system can demonstrate that related parts of long documents are available as focused memory units rather than only whole documents.

### Explicitly Out of Scope

- User-facing natural language answers.
- Advanced ranking.
- Hybrid retrieval.
- Re-ranking.
- Saved questions.
- Conversation memory.
- Personal annotations.
- Multiple memory strategies.

## 7. Milestone 4: Memory Construction

### Goal

The system can build searchable Memory from chunks while preserving source traceability.

### Why This Milestone Exists

Chunks are meaningful units, but they are not searchable memory by themselves. This milestone builds Memory from chunks so the product can later construct Evidence by meaning rather than exact wording.

The product is not an embedding system. It is a memory system. Embedding providers generate vectors as an infrastructure mechanism; the application builds Memory as the business concept.

### Product Capabilities Delivered

- Chunks can be transformed into Memory records.
- Each Memory record remains linked to its Chunk and original Source.
- Memory records store the model identifier, dimensions, provider, fingerprint, and creation metadata needed for engineering review.
- Vector storage remains hidden behind infrastructure boundaries.
- The system can show which chunks have Memory prepared.
- Repeated Memory construction over unchanged chunks is stable and idempotent.

### Acceptance Criteria

- A user can import, extract, chunk, and build Memory for a representative set of job search materials.
- The system can show which chunks have associated Memory.
- The system preserves the relationship between Source, SourceContent, Chunk, and Memory.
- The system does not expose embeddings as a domain entity.
- The system records enough technical metadata to explain how Memory was built.

### Explicitly Out of Scope

- Similarity search.
- Evidence construction.
- Generated natural language answers.
- Hybrid retrieval.
- Re-ranking.
- Multiple memory strategies.
- Prompt assembly.
- Answer generation.

## 8. Milestone 5: Evidence Construction

### Goal

The system can construct Evidence from searchable Memory when the user asks a job search question.

### Why This Milestone Exists

This is the first milestone where the product starts behaving like intelligent memory instead of organized storage.

The system should prove that a user can ask about concepts such as AWS, English, remote work, architecture, Docker, Kubernetes, messaging, or system design and receive relevant source-backed evidence before any generated answer exists.

### Product Capabilities Delivered

- Users can ask natural language questions over searchable Memory.
- The system constructs Evidence candidates from the user's materials.
- Evidence remains linked to Source, SourceContent, Chunk, and Memory.
- The system can return evidence even before producing a polished answer.
- The system can say when no useful evidence is found.
- The system supports concept-oriented Evidence construction where wording differs across sources.

### Acceptance Criteria

- A user can ask questions such as:
  - Which companies required AWS?
  - Which opportunities required English?
  - Which recruiter mentioned remote work?
  - Which interviews discussed system design?
  - Which companies mentioned asynchronous messaging?
- The system returns relevant source excerpts or sections for supported questions.
- The system identifies the source material behind each Evidence result.
- The system returns a clear insufficient-evidence result when the Memory does not support the question.
- The user can verify Evidence without manually opening every imported material.

### Explicitly Out of Scope

- Generated natural language answers.
- Interview coaching.
- Resume rewriting.
- Application tracking.
- Chat history.
- Re-ranking.
- Advanced analytics.
- Market-wide claims beyond imported material.

## 9. Milestone 6: Grounded Question Answering

### Goal

The system can answer user questions using Evidence and clearly show what supports the answer.

### Why This Milestone Exists

Evidence alone gives users support, but the product vision requires a useful memory interface. This milestone adds the final answer layer while preserving the core rule: evidence comes first.

The system should feel like consulting the user's own job search memory, not like asking a generic assistant.

### Product Capabilities Delivered

- Users receive concise answers to supported job search questions.
- Answers are generated only from Evidence-backed context.
- Answers include visible evidence.
- The system separates supported facts from interpretation.
- The system admits when evidence is missing, weak, or ambiguous.
- The system can partially answer questions when only partial evidence exists.

### Acceptance Criteria

- A user can ask at least five realistic job search questions and receive grounded answers when evidence exists.
- Each substantive answer includes source evidence.
- Unsupported questions produce an honest "not enough information" result.
- Partial evidence results are communicated clearly.
- The answer does not claim knowledge from outside imported material.
- The user can inspect the evidence behind an answer.

### Explicitly Out of Scope

- Autonomous agents.
- Proactive recommendations.
- Resume or cover letter generation.
- Interview performance scoring.
- Salary negotiation coaching.
- Chat history as memory.
- Personalization beyond imported materials.
- Multi-user review workflows.

## 10. Complete MVP Memory Loop

### Goal

The product can demonstrate the full MVP loop from imported job search material to grounded answers with evidence after Milestone 6.

### Why This Milestone Exists

The MVP is successful only when all previous capabilities work together as one coherent product experience.

This completion check validates the educational value of the architecture and confirms that the system solves the original problem: finding knowledge, not merely finding documents.

### Product Capabilities Delivered By The MVP

- Users can import a representative job search collection.
- Users can see processing and search-readiness status.
- Users can ask natural language questions across the collection.
- Users can construct Evidence across multiple source types.
- Users can receive grounded answers with source references.
- Users can understand when the system cannot answer.
- The product can demonstrate the difference between keyword search and concept-oriented memory.
- The product can be evaluated using the success metrics from the product requirements.

### Acceptance Criteria

- The full loop can be demonstrated end to end:
  - Import materials.
  - Prepare searchable memory.
  - Ask a question.
  - Construct Evidence.
  - Generate a grounded answer.
  - Review supporting sources.
- The product can answer the core MVP examples when source material supports them:
  - Which companies required AWS?
  - Which opportunities required English?
  - Which recruiter talked about architecture?
  - Have I answered this interview question before?
  - Which companies mentioned Docker and Kubernetes?
- The product clearly distinguishes:
  - Answered with evidence.
  - Partially answered.
  - Unable to answer from available material.
  - Source not searchable yet.
- Import failures and partial processing remain visible.
- Repeated questions over unchanged material return stable core findings.
- The MVP remains focused on job search memory rather than becoming a general chatbot or career assistant.

### Explicitly Out of Scope

- Authentication.
- User accounts.
- Dashboards.
- AI agents.
- Chat history.
- Multi-user collaboration.
- OCR.
- Multiple memory-building providers or strategies.
- Re-ranking.
- Deployment.
- Analytics.
- Observability dashboards.
- External account synchronization.
- Advanced career coaching.

## 11. Future Evolution After MVP

The following capabilities are intentionally deferred until after the MVP proves the complete memory loop:

- OCR for scanned or image-based documents.
- Additional document formats.
- Multiple memory strategies.
- Hybrid retrieval.
- Re-ranking.
- Personal annotations.
- Saved questions.
- Conversation memory.
- Semantic filters.
- Richer opportunity profiles.
- Collaboration with mentors or coaches.
- External integrations with explicit consent.
- Advanced reporting across the user's own search history.

These capabilities should only be considered after the MVP demonstrates that users can import job search material, build searchable memory, ask questions, construct Evidence, and receive grounded answers.

## 12. Critical Review

This roadmap was reviewed against the approved product requirements and architecture.

### 12.1 Complexity Check

The roadmap avoids advanced capabilities such as agents, dashboards, collaboration, OCR, multiple memory strategies, re-ranking, deployment, and analytics.

The milestones build one complete product loop before adding future sophistication.

### 12.2 Product Value Check

Each milestone delivers visible product progress:

- Milestone 1: users can collect and track job search material.
- Milestone 2: users can verify that imported material is readable.
- Milestone 3: users can review chunks created from their material.
- Milestone 4: users can see which chunks have Memory built.
- Milestone 5: users can construct Evidence for real questions.
- Milestone 6: users can receive grounded answers.

### 12.3 Architecture Alignment Check

The roadmap follows the two approved flows:

- Knowledge Ingestion: milestones 1, 2, 3, and 4.
- Evidence and Answering: milestones 5 and 6.

It also preserves the approved architecture principles:

- Memory first.
- Evidence before generation.
- Evidence before answers.
- Clear lifecycle states.
- Source traceability.
- Cautious unsupported-question behavior.

### 12.4 Scope Check

The roadmap does not introduce product areas outside the MVP. It remains focused on helping a single user construct grounded Evidence and answers from their own job search materials.
