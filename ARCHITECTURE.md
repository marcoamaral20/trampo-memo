# Architecture: AI-Powered Job Search Memory

## 1. Architecture Summary

This system is an AI-powered memory for job search materials.

Its purpose is to help users find grounded knowledge from their own resumes, job descriptions, company materials, recruiter conversations, interview feedback, personal notes, and copied or exported email content.

The architecture follows one central rule:

> The system must build and search memory before it generates an answer.

The answer generation layer is intentionally last. It does not own the truth of the system. It receives selected context, evidence, and instructions after the application has constructed Evidence from Memory.

The architecture is organized around two independent flows:

- Ingestion Flow: transforms imported material into searchable memory.
- Query Flow: transforms a user question into Evidence and a grounded answer.

These flows should be understandable, observable, and evolvable independently.

## 2. Architectural Principles

### 2.1 Memory First. AI Second.

The durable value of the product is the user's searchable memory, not the final generated response.

The system should preserve source material, derived chunks, metadata, Evidence records, and evidence references so that answers can be verified.

### 2.2 Evidence Before Generation.

The system must construct Evidence from Memory before asking the answer generation layer to respond.

This keeps the generated answer grounded in the user's own materials instead of relying on general knowledge or unsupported inference.

### 2.3 Evidence Before Answers.

Every substantive answer should be backed by source evidence.

If evidence is insufficient, the system should say so. Missing evidence is a valid result.

### 2.4 Simple Components With Clear Responsibilities.

Each module should do one major job:

- Import materials.
- Extract text.
- Split text.
- Represent text for semantic search.
- Store memory.
- Retrieve relevant context.
- Assemble evidence.
- Generate grounded answers.

The architecture should be easy to explain without requiring low-level technical detail.

### 2.5 Explainability Over Magic.

The system should expose why an answer was produced:

- Which sources were used.
- Which excerpts were relevant.
- What the answer can and cannot claim.
- When the source material is ambiguous or incomplete.

### 2.6 Modular Design.

Ingestion, Evidence construction, answer generation, evidence handling, and source review should be separate concerns.

This separation allows the system to improve one area without rewriting the whole product.

### 2.7 Incremental Evolution.

The MVP should prove the full lifecycle with a small, understandable delivery path.

Future capabilities should fit naturally into the same lifecycle rather than requiring a new architecture.

### 2.8 Production-Oriented Thinking.

The system should make operational states visible:

- Imported.
- Processing.
- Searchable.
- Failed.
- Partially processed.
- Answered with evidence.
- Unable to answer from available evidence.

Reliability, privacy, recoverability, and observability are product concerns, not technical afterthoughts.

### 2.9 Technology Agnostic.

The architecture describes responsibilities, boundaries, and information flow. It does not depend on concrete technical choices.

## 3. System Overview

At a high level, the system has four layers:

### 3.1 Source Layer

The source layer contains the original materials imported by the user.

Examples:

- PDF documents.
- Markdown files.
- Plain text files.
- Job descriptions.
- Company information.
- Recruiter conversations.
- Interview feedback.
- Personal notes.
- Copied or exported email content.

The source layer preserves the user's original context.

### 3.2 Memory Preparation Layer

The memory preparation layer transforms imported material into searchable memory.

It extracts readable text, normalizes content, splits content into meaningful chunks, builds Memory from those chunks, and stores source metadata.

### 3.3 Evidence Construction Layer

The Evidence Construction layer produces question-specific Evidence from Memory.

It may use retrieval algorithms internally, but Retrieval is not a domain concept. Memory exists independently of questions. Evidence exists because of a question.

### 3.4 Answer Layer

The answer layer receives the user question, Evidence, selected context, and answer rules.

It produces a grounded response that references the evidence used and identifies when available information is insufficient.

## 4. Major Modules

### 4.1 Import Module

Responsible for accepting user-provided materials.

Responsibilities:

- Receive supported file and text-based inputs.
- Preserve original source identity.
- Create an import record for each user-provided material.
- Communicate initial import status.
- Avoid mixing materials from unrelated imports.
- Pass imported material to document processing.

This module should not decide what an answer means. It only starts the memory-building process.

### 4.2 Document Processing Module

Responsible for turning imported materials into clean readable text.

Responsibilities:

- Extract text from supported source formats.
- Preserve source-level context such as title, origin, content type, and date when available.
- Detect extraction failures or partial extraction.
- Mark material as failed or partially processed when needed.
- Pass extracted text to chunking.

This module protects the rest of the system from format-specific complexity.

### 4.3 Chunking Module

Responsible for splitting extracted text into smaller meaningful units.

Responsibilities:

- Break long materials into searchable chunks.
- Preserve each chunk's connection to the original source.
- Preserve enough surrounding context for later evidence review.
- Avoid chunks that are too large to be useful or too small to be meaningful.
- Support future chunking strategies without changing Evidence construction or answer generation.

Chunking is a memory design decision, not a text formatting detail. Poor chunks create poor memory.

### 4.4 Memory Module

Responsible for building searchable Memory from chunks.

Responsibilities:

- Transform each chunk into a Memory record that can later support meaning-based Evidence construction.
- Keep each Memory record linked to its source chunk.
- Track the model, dimensions, provider, fingerprint, and creation metadata needed to reproduce how Memory was built.
- Hide embedding vectors and vector storage behind infrastructure boundaries.
- Allow future memory-building strategies without changing imported source records or chunk records.

Memory is the business concept. Embedding generation is an infrastructure concern used to build Memory. Vector storage is an infrastructure concern used to store and search Memory. The product never exposes embeddings as a domain entity.

The provider generates vectors. The application builds Memory.

This module enables concept search, such as connecting "messaging" with RabbitMQ, Kafka, Amazon SQS, BullMQ, event queues, or asynchronous communication.

### 4.5 Metadata Store Module

Responsible for preserving product and source context.

Responsibilities:

- Store source document records.
- Store chunk records and their source relationships.
- Store import and processing status.
- Store document type, title, date, origin, and other available source descriptors.
- Store answer and Evidence trace information when useful for review.
- Support filters based on product concepts such as company, recruiter, role, interview, topic, or work model when those concepts are available.

The metadata store gives the system traceability, reviewability, and product context.

### 4.6 Evidence Construction Module

Responsible for turning a user question into Evidence.

Responsibilities:

- Interpret the user question as an Evidence construction request.
- Use retrieval algorithms internally to search Memory.
- Apply available metadata constraints when appropriate.
- Gather candidate Memory records.
- Construct Evidence records with relevance information.
- Preserve trace information so Evidence construction can be inspected.

The Evidence Construction module should prefer relevant Evidence over broad recall. It should not generate final answers.

### 4.7 Context Assembly Module

Responsible for preparing Evidence for answer generation.

Responsibilities:

- Combine selected chunks into a coherent answer context.
- Keep source references attached to each excerpt.
- Remove clearly irrelevant or duplicate context when possible.
- Respect answer boundaries, such as "only answer from imported material."
- Include enough evidence for a grounded response without overwhelming the answer layer.

This module is the bridge between Evidence and generation.

### 4.8 Prompt Assembly Module

Responsible for preparing the answer request given to the generation layer.

Responsibilities:

- Combine the user question, Evidence-backed context, evidence references, and answer rules.
- State that the answer must use only provided context.
- Include instructions for handling insufficient or ambiguous evidence.
- Preserve source references so the final answer can cite supporting material.
- Keep generation focused on the user's job search memory.

This module turns Evidence into an answer-ready package without creating the answer itself.

### 4.9 Answer Generation Module

Responsible for producing the final natural language answer.

Responsibilities:

- Answer the user's question using the assembled prompt and context.
- Separate supported facts from interpretation.
- State when evidence is insufficient.
- Avoid unsupported speculation.
- Keep the answer concise and useful.
- Reference the evidence returned by the evidence module.

This module is not allowed to read raw documents directly. It only receives selected context and evidence prepared by earlier modules.

### 4.10 Evidence Module

Responsible for making answer support visible to the user.

Responsibilities:

- Identify which source documents support an answer.
- Expose relevant excerpts or source sections.
- Connect each answer claim to evidence when practical.
- Make unsupported or uncertain answers explicit.
- Help users verify answers without manually searching every document.

Evidence is a first-class product output, not an internal debug detail.

### 4.11 Query Interface Module

Responsible for receiving user questions and returning grounded results.

Responsibilities:

- Accept natural language questions.
- Start the query flow.
- Return answers, evidence, and unsupported-question states.
- Communicate failures clearly.
- Keep the interaction focused on the user's imported materials.

This module should not bypass Evidence construction or ask the answer generation layer to answer directly from the question alone.

### 4.12 Status and Observability Module

Responsible for making lifecycle state visible.

Responsibilities:

- Track import, processing, and search-readiness states.
- Track failures and partial processing.
- Track whether answers were produced with evidence.
- Support review of Evidence construction and answer behavior.
- Help identify when poor answers come from missing material, failed processing, weak Evidence construction, or insufficient evidence.

This module supports production reliability and the educational purpose of the project.

## 5. Data Flow

## 5.1 Ingestion Flow

The ingestion flow builds memory from user-provided material.

```text
User imports material
        |
        v
Import Module records source identity and import status
        |
        v
Document Processing extracts readable text
        |
        v
Processing status is updated
        |
        v
Chunking splits text into meaningful units
        |
        v
Metadata Store records source, chunk, and status relationships
        |
        v
Memory Module builds searchable Memory from chunks
        |
        v
Material becomes searchable memory
```

### Ingestion Flow Rules

- Original source material must remain traceable.
- Text extraction can succeed, partially succeed, or fail.
- Chunking must preserve source relationships.
- Memory building should be independent from chunk creation.
- Memory should only be marked searchable when required processing steps are complete.
- Failures should be visible and recoverable.
- Ingestion should not block the user's ability to continue using already searchable memory.

## 5.2 Query Flow

The query flow answers questions from searchable memory.

```text
User asks a question
        |
        v
Query Interface records the question
        |
        v
Evidence Construction searches Memory using an internal retrieval algorithm
        |
        v
Evidence records are constructed
        |
        v
Context Assembly selects and organizes evidence
        |
        v
Prompt Assembly prepares question, context, evidence, and answer rules
        |
        v
Answer Generation receives the assembled prompt
        |
        v
Grounded answer is produced
        |
        v
Evidence sources and excerpts are attached
        |
        v
Answer, evidence, and limitations are returned to the user
```

### Query Flow Rules

- Evidence must be constructed before answer generation.
- The answer generation module should not answer from the user's question alone.
- Every substantive answer should include evidence.
- If Evidence Construction finds no useful evidence, the system should say that the available material does not answer the question.
- If evidence is partial or ambiguous, the answer should say so.
- The user should be able to inspect the source material behind the answer.

## 6. Domain Model

These are product concepts, not storage tables.

The core domain progression is:

```text
Source
        |
        v
SourceContent
        |
        v
Chunk
        |
        v
Memory
        |
        v
Evidence
        |
        v
Answer
```

### 6.1 Source

An original material imported by the user.

Examples:

- A resume.
- A job description.
- A company PDF.
- Interview feedback.
- Recruiter conversation notes.
- Personal notes.
- Copied or exported email content.

Key meaning: the Source is the root of trust for evidence.

### 6.2 Import Record

The lifecycle record for a user import.

It tracks whether the imported material was accepted, processed, partially processed, failed, or made searchable.

Key meaning: the import record explains the operational state of the source.

### 6.3 SourceContent

The readable normalized text derived from a Source.

Key meaning: SourceContent is the bridge between raw source material and chunks.

### 6.4 Chunk

A meaningful segment of SourceContent.

Each chunk remains linked to its SourceContent, Source, and surrounding context.

Key meaning: chunks are the units used to build Memory and later construct Evidence.

### 6.5 Memory

A searchable representation of a Chunk.

Memory keeps the product relationship to the Chunk, model identifier, dimensions, provider, fingerprint, and creation metadata needed to understand how it was built.

Key meaning: Memory is the product concept that lets the system later find related ideas even when exact words differ. Embedding vectors are an internal mechanism used to build Memory, not a domain entity.

### 6.6 Knowledge Source

A Source or Chunk that can support an answer.

Key meaning: knowledge sources are evidence candidates.

### 6.7 Query

A user's natural language question.

Examples:

- Which companies required AWS?
- Which recruiter mentioned remote work?
- Have I answered this interview question before?

Key meaning: the query starts Evidence construction, not generation.

### 6.8 Evidence

A question-specific support record constructed from Memory.

Evidence preserves the relationship to Memory, Chunk, SourceContent, and Source. It also preserves the user question, excerpt, rank, relevance score, and trace metadata needed to understand why it was selected.

Key meaning: Evidence is the product concept users can inspect. Retrieval is only the internal algorithm used to construct it.

### 6.9 Assembled Prompt

The answer-ready package that combines the user's question, Evidence, selected context, and answer rules.

Key meaning: the assembled prompt constrains generation to Evidence-backed memory.

### 6.10 Evidence Reference

A connection between an answer claim and the source material that supports it.

Key meaning: evidence references make the answer verifiable.

### 6.11 Answer

The final response returned to the user.

An answer may be:

- Supported by evidence.
- Partially supported.
- Unable to answer from available material.

Key meaning: an answer is only as trustworthy as the evidence behind it.

### 6.12 Evidence Trace

A reviewable record of how a query moved through Evidence construction and context assembly.

Key meaning: Evidence traces support debugging, evaluation, and education without making Retrieval a domain concept.

## 7. Architectural Decisions

## ADR 1: Answers Must Always Include Evidence

### Decision

Every substantive answer should include source evidence or clearly state that evidence is insufficient.

### Context

The product handles sensitive and high-impact job search information. Users may use answers to prepare for interviews, compare opportunities, or follow up with recruiters.

### Rationale

Evidence makes the system trustworthy. It also reinforces the product vision: users are consulting their own memory, not receiving unsupported advice.

### Trade-offs

- Pros: Higher trust, easier verification, better debugging, stronger product differentiation.
- Cons: Answers may feel less conversational, and some responses may be shorter or more cautious than users expect.

## ADR 2: Evidence Construction Happens Before Generation

### Decision

The system must construct Evidence from Memory before generating an answer.

### Context

The user's question is often about private imported material, not general knowledge.

### Rationale

Evidence-first behavior keeps answers grounded. Retrieval algorithms may be used internally, but the business result is Evidence. This reduces unsupported speculation and makes missing evidence visible.

### Trade-offs

- Pros: Better grounding, clearer limitations, easier evaluation.
- Cons: Answer quality depends heavily on ingestion, chunking, memory-building, Evidence construction, and the retrieval algorithms used internally.

## ADR 3: The Answer Generation Layer Never Reads Raw Documents Directly

### Decision

The answer generation layer receives assembled context and evidence, not unrestricted access to raw documents.

### Context

Raw documents may be long, noisy, duplicated, sensitive, or irrelevant to a specific question.

### Rationale

Restricting answer generation to Evidence-backed context keeps the system explainable and reduces accidental unsupported claims. It also makes Evidence quality easier to evaluate.

### Trade-offs

- Pros: Better control, smaller context, clearer evidence boundaries.
- Cons: If Evidence construction misses relevant material, the answer layer cannot recover by scanning everything.

## ADR 4: Chunking Is Independent From Memory Building

### Decision

The system treats chunk creation and Memory building as separate responsibilities.

### Context

Chunking decides what counts as a useful unit of memory. Memory building decides how that unit becomes searchable by meaning.

### Rationale

Separating these responsibilities keeps the architecture flexible. The system can improve chunking without changing memory-building strategy, or change vector-generation providers without rethinking source extraction.

### Trade-offs

- Pros: Clearer responsibilities, easier experimentation, better incremental evolution.
- Cons: More lifecycle states must be tracked during ingestion.

## ADR 5: Metadata and Memory Storage Are Separate Concerns

### Decision

The system separates source and product metadata from the infrastructure used to store searchable Memory.

### Context

The product needs both meaning-based Evidence construction and traceable source context.

### Rationale

Memory is the business concept that represents a searchable chunk. Vector storage is optimized for finding semantically related chunks. Metadata is optimized for explaining source identity, status, type, date, company, recruiter, role, and other product concepts. Treating these concerns separately keeps each responsibility clear.

### Trade-offs

- Pros: Better traceability, easier filtering, cleaner mental model, stronger evidence support.
- Cons: Evidence construction must coordinate domain metadata with vector-storage infrastructure.

## ADR 6: Document Ingestion Is Asynchronous

### Decision

Importing a document should create an import record quickly, while heavier preparation happens as a separate lifecycle.

### Context

Documents may vary in size, format, quality, and extraction difficulty.

### Rationale

Asynchronous ingestion makes the product more reliable and honest. Users can see whether material is processing, searchable, partially processed, or failed.

### Trade-offs

- Pros: Better user feedback, easier recovery, more scalable processing model.
- Cons: Newly imported material may not be searchable immediately.

## ADR 7: Searchable Memory Is Built From Chunks, Not Whole Documents

### Decision

The system builds searchable Memory from smaller document chunks rather than treating each full document as one memory unit.

### Context

Job descriptions, company materials, and notes may contain many unrelated facts.

### Rationale

Chunk-level memory improves Evidence quality. A question about English requirements should produce Evidence from the relevant section, not an entire job description full of unrelated requirements.

### Trade-offs

- Pros: More precise Evidence, better evidence excerpts, clearer answers.
- Cons: Poor chunking can separate related context or create fragments that are too small to interpret.

## ADR 8: The System Should Prefer Cautious Answers Over Unsupported Answers

### Decision

When evidence is missing, weak, or ambiguous, the system should say so instead of filling gaps.

### Context

The user may act on the product's answer during a real job search.

### Rationale

A cautious answer preserves trust and aligns with the product principle that missing evidence is acceptable.

### Trade-offs

- Pros: Higher trust, fewer misleading claims, clearer user expectations.
- Cons: The system may feel less impressive than a general chatbot.

## ADR 9: Import Status Is Part of the Product Architecture

### Decision

The system must explicitly track and expose import and processing status.

### Context

Users need to understand whether a missing answer means "the information is not present" or "the material has not been processed yet."

### Rationale

Status visibility prevents false confidence and supports recoverability.

### Trade-offs

- Pros: Better user trust, clearer debugging, more transparent product behavior.
- Cons: Adds lifecycle complexity that must be represented consistently.

## ADR 10: The MVP Supports One Complete Loop Before Advanced Search Features

### Decision

The MVP should prioritize a complete ingestion-to-answer lifecycle before adding advanced Evidence construction enhancements.

### Context

The project is educational and should demonstrate a real-world RAG system without becoming too broad too early.

### Rationale

A complete, understandable loop teaches the architecture better than a partially implemented advanced system.

### Trade-offs

- Pros: Faster validation, clearer roadmap, lower complexity, better learning value.
- Cons: Early Evidence quality may be limited compared with future versions.

## 8. Operational States

The architecture should support these states:

### 8.1 Source States

- Imported: material has been received.
- Processing: text and memory preparation are in progress.
- Searchable: material can participate in Evidence construction.
- Partially processed: some content is searchable, but limitations exist.
- Failed: material could not be prepared for search.

### 8.2 Query States

- Answered with evidence: the system found enough support to answer.
- Partially answered: the system found some evidence, but not enough for a complete answer.
- Unable to answer: the available searchable memory does not support an answer.
- Query failed: the system could not complete the query flow.

These states help users understand whether a result reflects the source material or the system lifecycle.

## 9. Error Handling and Recovery

The architecture should make failures explicit and recoverable.

### 9.1 Ingestion Failures

Examples:

- Unsupported source format.
- Text extraction failure.
- Empty or unreadable content.
- Partial extraction.
- Memory-building failure.

Expected behavior:

- Preserve the source record when possible.
- Mark the failure state clearly.
- Explain the failure in user-facing terms.
- Allow retry or replacement in a future version.
- Prevent failed material from being treated as searchable.

### 9.2 Query Failures

Examples:

- No relevant memory found.
- Only weak or ambiguous evidence found.
- Context assembly cannot create a reliable answer context.
- Answer generation cannot complete.

Expected behavior:

- Return a clear state instead of pretending to answer.
- Preserve evidence candidates when useful.
- Distinguish "no evidence found" from "system could not complete the query."

## 10. Observability and Evaluation

The system should be observable enough to support production operation and educational learning.

Important questions the architecture should help answer:

- Which sources are searchable?
- Which imports failed or partially succeeded?
- Which chunks supported an answer?
- Which query produced insufficient evidence?
- Did the answer include evidence?
- Was missing information caused by absent source material, failed ingestion, weak Evidence construction, or answer-layer refusal?

Evaluation should focus on product outcomes:

- Can users find company, role, recruiter, skill, language, work model, interview, and feedback information?
- Are answers grounded in visible evidence?
- Does the system admit when it cannot answer?
- Are repeated questions over the same memory stable in their core findings?

## 11. Privacy and Data Boundaries

The system handles private job search data. Architecture must preserve boundaries around user-owned material.

Core rules:

- Source material belongs to the user.
- Imported content should not be exposed outside the user's own memory experience.
- Evidence should only reference the user's imported materials.
- Future sharing or collaboration must require explicit product decisions and consent.
- Generated answers should not imply access to information outside imported material.

Privacy is not only a security property. It is part of user trust and product correctness.

## 12. Future Evolution

The architecture should support future capabilities without requiring a new mental model.

### 12.1 Multiple Memory-Building Strategies

The Memory module can evolve to support different strategies for different content types or quality requirements.

The current architecture allows this because Memory building is separate from source documents and chunks.

### 12.2 Multiple Vector Storage Providers

Vector storage can evolve behind the Memory infrastructure boundary.

The rest of the product should care about retrieving relevant Memory, not about which storage provider performs the search.

### 12.3 Hybrid Retrieval

Future Evidence construction may combine meaning-based search, keyword search, metadata filters, and domain-specific ranking.

The current architecture allows this because retrieval remains an internal mechanism behind Evidence construction and can coordinate multiple search signals without changing the domain language.

### 12.4 Re-ranking

Future versions may add a second selection step after initial memory search to improve context quality.

This fits naturally between Evidence construction and context assembly.

### 12.5 OCR

Future versions may support image-based or scanned documents.

This fits inside document processing without changing Evidence construction or answer generation.

### 12.6 Additional Document Formats

Future input formats can be added through the import and document processing modules.

The rest of the architecture remains focused on extracted text, chunks, Memory, Evidence, and Answers.

### 12.7 Conversation Memory

Future versions may store prior user questions and answers as part of the user's memory experience.

This should remain separate from source documents unless the user explicitly chooses to treat conversations as searchable material.

### 12.8 Personal Annotations

Users may later annotate sources, chunks, or answers.

Annotations can become metadata and evidence context without changing the ingestion-to-query lifecycle.

### 12.9 Semantic Filters

Future versions may let users filter by concepts such as company, recruiter, role, seniority, work model, language, topic, or interview stage.

This fits the metadata and Evidence construction boundaries already described.

## 13. MVP Architecture Boundary

The MVP should include one complete, production-shaped loop:

- Import supported job search material.
- Extract readable text.
- Split text into meaningful chunks.
- Build searchable Memory from chunks.
- Preserve source and chunk metadata.
- Ask a natural language question.
- Retrieve relevant chunks.
- Assemble answer context.
- Assemble a constrained prompt.
- Generate a grounded answer.
- Return answer evidence.
- Communicate insufficient evidence honestly.
- Expose import and query states.

The MVP should not include advanced coaching, automatic applications, collaboration, external account synchronization, dashboards, or market-wide claims.

## 14. Architecture Review Notes

This document intentionally stays at the architecture level. It avoids:

- Vendor-specific decisions.
- Low-level technical choices.
- Storage product decisions.
- Project layout decisions.
- Detailed storage design.
- Low-level contracts.

The design is intentionally modular without adding unnecessary system boundaries. The modules are responsibility boundaries and conceptual units.

The approved product requirements are reflected through the two main flows: ingestion builds traceable Memory from user-owned material, and querying constructs Evidence from that Memory before producing an answer.

## 15. Architecture Principle Summary

- Ingestion Flow: preserve source material, extract text, create meaningful chunks, build searchable Memory, and keep status visible.
- Query Flow: construct Evidence from Memory, assemble context, constrain generation, return grounded answers, and treat missing evidence as a valid result.
