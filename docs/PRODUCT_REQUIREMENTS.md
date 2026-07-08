# Product Requirements: AI-Powered Job Search Memory

## 1. Problem Statement

Job searches generate a large amount of fragmented information across resumes, job descriptions, company materials, recruiter conversations, interview feedback, personal notes, and emails.

At first, the challenge is organizing documents. After a few weeks, the harder problem becomes retrieving specific knowledge from those documents.

Users need to answer questions such as:

- Which companies required AWS?
- Which opportunities required English?
- Which recruiter mentioned remote work?
- Which interview focused on system design?
- Have I already answered this interview question before?

Traditional keyword search is insufficient because the same concept can appear under many different names. For example, a user may care about "messaging", while the source material mentions RabbitMQ, Kafka, Amazon SQS, BullMQ, event queues, or asynchronous communication.

The product must help users search meaning, context, and accumulated knowledge, not just document text.

## 2. Product Vision

The product is an intelligent memory for job search activity.

It should ingest heterogeneous career-search materials, transform them into organized knowledge, and allow users to ask natural language questions about everything they have collected or experienced during the search.

The product is not intended to be another general-purpose chatbot. The conversational layer is only the access point. The core value is the memory itself: structured, traceable, searchable knowledge grounded in the user's own job search materials.

The product is also not an embedding system. Embeddings may be used internally to build searchable memory, but they are an implementation mechanism, not the product language or the user-facing value.

The product should help users:

- Recall details from past opportunities.
- Compare companies and roles.
- Prepare for interviews using their own history.
- Avoid repeating work.
- Identify patterns across job descriptions, feedback, and conversations.
- Preserve context that would otherwise disappear across files, notes, and message threads.

## 3. Target Users

The initial target users are individual job seekers who manage multiple opportunities at the same time and need to reason across a growing body of job search information.

The strongest early fit is for users whose search includes:

- Multiple companies or roles in parallel.
- Technical job descriptions with overlapping terminology.
- Interview loops with recurring questions and feedback.
- Recruiter conversations spread across different channels.
- Personal notes written over several weeks or months.
- A need to prepare, compare, and remember accurately.

Secondary audiences include career coaches, mentors, and educators who help candidates review their search history, provided the product remains centered on the candidate's own materials and consent.

## 4. User Personas

### 4.1 Technical Job Seeker

A software professional applying to many engineering roles. They collect job descriptions, company pages, recruiter messages, interview notes, and technical preparation notes.

Primary needs:

- Find which companies ask for specific technical concepts.
- Compare role expectations across companies.
- Reuse previous interview preparation.
- Track which questions and topics have already appeared.

### 4.2 Career Switcher

A candidate transitioning into a new role or industry. They may be learning the language of the market while applying.

Primary needs:

- Understand recurring requirements across opportunities.
- Translate unfamiliar terminology into practical themes.
- Identify skill gaps based on real job descriptions.
- Keep notes and feedback connected to each opportunity.

### 4.3 Interview-Heavy Candidate

A candidate currently in several interview processes. They receive feedback, assignments, take-home instructions, and recruiter updates from multiple companies.

Primary needs:

- Recall interview details quickly.
- Avoid confusing one company with another.
- Prepare for follow-up rounds using previous notes.
- Track whether a topic, question, or concern has appeared before.

### 4.4 Career Coach or Mentor

A trusted advisor helping a candidate review opportunities and preparation material.

Primary needs:

- Help the candidate identify patterns.
- Review prior feedback and recurring themes.
- Support preparation without manually reading every document.
- Maintain clear separation between the candidate's source material and generated interpretation.

## 5. User Journey

### 5.1 Collect

The user gathers job search materials over time. These may include documents, notes, copied job descriptions, interview feedback, recruiter conversations, emails, and company information.

### 5.2 Import

The user imports materials into the product. The product should accept common text-oriented job search artifacts and preserve the original source context.

### 5.3 Organize

The product processes imported materials into searchable knowledge. The user should not need to manually tag every item for the system to become useful, but the product should preserve enough source information to support trust and review.

### 5.4 Ask

The user asks natural language questions about their job search memory.

Examples:

- Which companies required AWS?
- Which opportunities mentioned English?
- Which recruiter talked about architecture?
- Which companies mentioned Docker and Kubernetes?
- Have I answered this system design question before?

### 5.5 Review Evidence

The product answers with relevant findings and shows where the information came from. The user can inspect the source material behind an answer.

### 5.6 Act

The user uses the answer to prepare for an interview, prioritize applications, update a resume, compare companies, or follow up with a recruiter.

## 6. Pain Points

- Information is scattered across many formats and channels.
- Keyword search misses related concepts expressed with different wording.
- Similar companies, roles, and interview processes blur together over time.
- Candidates repeat preparation work because they cannot easily find prior answers.
- Recruiter conversations contain useful details but are hard to search later.
- Job descriptions are long, repetitive, and difficult to compare manually.
- Interview feedback often stays disconnected from the job description or company context.
- Users may not trust an AI answer unless they can verify the source.
- Overly broad chatbot behavior can produce confident but unsupported answers.

## 7. Goals

### 7.1 Product Goals

- Help users retrieve knowledge from their job search history using natural language.
- Preserve source traceability for every answer.
- Support practical job search decisions, not generic conversation.
- Make related concepts discoverable even when exact words differ.
- Reduce repeated manual search and repeated interview preparation work.
- Provide a clear educational example of how an AI-assisted knowledge product should behave.

### 7.2 Experience Goals

- The user should feel they are consulting their own memory, not asking an unrelated assistant.
- Answers should be concise, grounded, and easy to verify.
- The product should distinguish between known information, likely related information, and missing information.
- The product should avoid pretending to know something that is not present in the user's materials.

### 7.3 Educational Goals

- Demonstrate a maintainable, explainable AI product workflow.
- Show that the AI response is the final access layer, not the entire system.
- Favor clarity and observable behavior over magical or opaque behavior.
- Support incremental improvement without changing the product's core promise.

## 8. Functional Requirements

### 8.1 Importing Materials

The MVP must allow users to import job search materials from:

- PDF documents.
- Markdown files.
- Plain text files.
- Job descriptions.
- Company information.
- Recruiter conversations.
- Interview feedback.
- Personal notes.
- Email content copied or exported by the user.

The product should preserve each imported item's source identity, such as title, origin, date when available, and content type when available.

### 8.2 Source Review

Users must be able to review imported materials after import.

At minimum, the product should make it possible to:

- See which materials have been imported.
- Identify the original source of an answer.
- Inspect the relevant source excerpt or section behind an answer.
- Understand when a question could not be answered from available material.

### 8.3 Knowledge Search

Users must be able to ask natural language questions about the imported material.

The product should support questions about:

- Companies.
- Roles.
- Required skills.
- Tools and technologies.
- Languages.
- Work model, such as remote, hybrid, or onsite.
- Recruiters.
- Interview topics.
- Interview questions.
- Feedback and concerns.
- Repeated themes across opportunities.

The product should identify conceptually related information even when exact terms differ.

### 8.4 Answer Behavior

Answers must be grounded in imported materials.

The product should:

- Answer directly when supporting evidence exists.
- Show the source or sources used to support the answer.
- Separate facts from interpretation.
- Say when the available material is insufficient.
- Avoid unsupported speculation.
- Prefer concise summaries over long generated essays.

### 8.5 Opportunity-Level Recall

The product should help users connect facts to specific opportunities.

Examples:

- A company required English.
- A role mentioned system design.
- A recruiter mentioned remote work.
- A job description listed AWS.
- An interview included architecture discussion.

### 8.6 Cross-Opportunity Comparison

The product should help users compare opportunities based on imported evidence.

Examples:

- Which companies mentioned cloud services?
- Which roles required both Docker and Kubernetes?
- Which interviews focused on software architecture?
- Which opportunities appear to require English communication?

### 8.7 Prior Answer Detection

The product should help users determine whether they have already addressed a question, topic, or interview theme in previous notes or materials.

The product does not need to judge whether a previous answer was good. It only needs to help the user find related prior material.

### 8.8 Import Status

Users should be able to understand whether imported material is ready to search.

The product should communicate:

- Imported successfully.
- Still being prepared for search.
- Failed to import.
- Imported with limitations.

### 8.9 Evidence-First Interaction

For every substantive answer, the product should make evidence visible enough that the user can verify it without manually searching the entire source collection.

## 9. Non-Functional Requirements

### 9.1 Explainability

The product must prioritize explainable answers. Users should understand why an answer was produced and what source material supports it.

### 9.2 Reliability

The product should behave predictably across repeated use. The same question over the same source material should produce consistent core findings, even if wording varies.

### 9.3 Data Integrity

Imported materials should not be silently lost, overwritten, or mixed with unrelated content.

### 9.4 Privacy

The product will handle sensitive personal and professional information. It must treat resumes, emails, recruiter conversations, feedback, and notes as private user data.

### 9.5 Observability

The product should make important operational states visible to the user or operator, especially import success, import failure, search readiness, and answer evidence.

### 9.6 Simplicity

The product should avoid unnecessary features in the MVP. Each feature must support the core promise of importing job search materials and retrieving grounded knowledge from them.

### 9.7 Incremental Evolution

The product should be designed as a learning project that can evolve step by step. The MVP should prove the core product behavior before adding broader automation, collaboration, or advanced career coaching features.

### 9.8 Deterministic Behavior Where Possible

The product should use predictable rules and explicit product behavior wherever practical, especially for import status, source attribution, answer boundaries, and unsupported-question handling.

## 10. MVP Scope

### 10.1 In Scope

The MVP includes:

- Importing supported job search materials.
- Preserving imported source context.
- Preparing imported materials for knowledge search.
- Asking natural language questions over imported materials.
- Returning grounded answers with visible evidence.
- Identifying related concepts even when wording differs.
- Supporting opportunity, company, recruiter, skill, language, work model, interview, and feedback queries.
- Communicating import status and failure states.
- Handling unsupported or unanswerable questions honestly.

### 10.2 MVP Example Questions

The MVP should support questions such as:

- Which companies required AWS?
- Which opportunities required English?
- Which recruiter talked about architecture?
- Have I answered this interview question before?
- Which companies mentioned Docker and Kubernetes?
- Which opportunities discussed remote work?
- Which interviews included system design?
- Which companies mentioned asynchronous messaging?

## 11. Out of Scope

The MVP will not include:

- Automatic job applications.
- Resume generation.
- Cover letter generation.
- Interview performance scoring.
- Salary negotiation coaching.
- Browser extensions.
- Calendar integration.
- Email account synchronization.
- Recruiter relationship management.
- Multi-user collaboration.
- Team administration.
- Public sharing of search results.
- Automated follow-up messages.
- Real-time notifications.
- Advanced analytics dashboards.
- Career coaching unrelated to imported source material.
- Claims about market-wide job trends beyond the user's own materials.

## 12. Success Metrics

### 12.1 User Value Metrics

- Users can find relevant opportunities, companies, recruiters, or interview notes faster than with manual search.
- Users can answer common preparation questions using their own prior materials.
- Users can verify answer evidence without opening many unrelated files.
- Users report reduced confusion between similar companies or interview processes.

### 12.2 Product Quality Metrics

- A high percentage of substantive answers include useful source evidence.
- Unsupported questions are clearly identified instead of answered speculatively.
- Imported materials have visible readiness status.
- Import failures are understandable and recoverable.
- Repeated questions over unchanged material return stable core findings.

### 12.3 MVP Validation Metrics

The MVP is successful if a user can:

- Import a representative set of job search materials.
- Ask at least five realistic job search questions.
- Receive grounded answers for questions supported by the imported material.
- See clear source evidence for each answer.
- Recognize when the product cannot answer from available material.

## 13. Risks

### 13.1 Overpromising Intelligence

The product may appear to promise complete understanding of the user's career search. This is risky because the system can only answer from imported and successfully prepared material.

Mitigation: communicate answer boundaries clearly and always expose evidence.

### 13.2 Unsupported Answers

The product may generate plausible answers that are not grounded in the user's materials.

Mitigation: require visible source evidence for substantive claims and clearly state when information is missing.

### 13.3 Source Quality Problems

Imported materials may be incomplete, outdated, duplicated, poorly formatted, or ambiguous.

Mitigation: preserve source context, communicate import limitations, and avoid treating unclear material as certain.

### 13.4 Privacy Sensitivity

Job search materials can include personal identity information, compensation expectations, private feedback, and confidential recruiter conversations.

Mitigation: keep privacy as a first-class product requirement and avoid features that share or expose information by default.

### 13.5 Scope Creep

The product could easily expand into resume optimization, application tracking, interview coaching, CRM, or market analytics.

Mitigation: keep the MVP focused on job search memory and grounded knowledge retrieval.

### 13.6 User Trust

If users cannot verify answers, they may stop trusting the product.

Mitigation: make evidence review a core interaction, not an optional advanced feature.

## 14. Known Limitations

- The MVP depends on the quality and completeness of imported materials.
- The product may miss relevant information when source text is vague, contradictory, or incomplete.
- The product may surface related information that still requires human judgment.
- The product will not know about opportunities, conversations, or feedback that were not imported.
- The product will not replace careful interview preparation.
- The product will not guarantee that all conceptually related terms are discovered.
- The product will not determine the truth of claims made in job descriptions or recruiter conversations.
- The product will not infer sensitive conclusions unless grounded in explicit source material.

## 15. Future Evolution

Future versions may include:

- Richer opportunity profiles assembled from multiple source materials.
- Manual correction and annotation of extracted knowledge.
- Saved questions and reusable preparation views.
- Interview preparation packs based on the user's own prior notes.
- Timeline views for companies, recruiters, and interview processes.
- Stronger duplicate detection across repeated job descriptions or notes.
- Deeper comparison between opportunities.
- User-defined concept groups, such as "cloud", "messaging", or "architecture".
- Personal knowledge hygiene tools for outdated or conflicting material.
- Optional integrations with external sources, only when privacy and consent are clear.
- Collaboration modes for candidates working with mentors or coaches.
- Advanced reporting about recurring requirements across the user's own search.

## 16. Product Principles

- Search knowledge, not files.
- Ground every answer in the user's own material.
- Treat missing evidence as an acceptable answer.
- Prefer clarity over magic.
- Preserve source context.
- Keep the MVP narrow enough to be understood, tested, and explained.
- Make the intelligent layer serve the memory, not replace it.
