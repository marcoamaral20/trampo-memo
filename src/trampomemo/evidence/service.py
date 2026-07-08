from hashlib import sha256
from uuid import NAMESPACE_URL, uuid5

from trampomemo.evidence.models import Evidence
from trampomemo.evidence.repository import EvidenceRepository
from trampomemo.memory.embedding_provider import EmbeddingProvider
from trampomemo.memory.repository import ALGORITHM_NAME, MemoryRepository


class EvidenceService:
    def __init__(
        self,
        *,
        memory_repository: MemoryRepository,
        evidence_repository: EvidenceRepository,
        provider: EmbeddingProvider,
    ) -> None:
        self.memory_repository = memory_repository
        self.evidence_repository = evidence_repository
        self.provider = provider

    def construct_evidence(self, *, question: str, limit: int) -> list[Evidence]:
        normalized_question = question.strip()
        question_fingerprint = _fingerprint(normalized_question)

        provider_result = self.provider.generate_vector(text=normalized_question)
        candidates = self.memory_repository.search_relevant(
            question=normalized_question,
            query_vector=provider_result.vector,
            limit=limit,
        )

        evidence = [
            Evidence(
                id=_stable_evidence_id(
                    question_fingerprint=question_fingerprint,
                    memory_id=candidate.memory.id,
                ),
                question=normalized_question,
                question_fingerprint=question_fingerprint,
                source_id=candidate.memory.source_id,
                source_content_id=candidate.chunk.source_content_id,
                chunk_id=candidate.chunk.id,
                memory_id=candidate.memory.id,
                excerpt=candidate.chunk.text,
                rank=rank,
                relevance_score=candidate.relevance_score,
                trace_metadata={
                    "algorithm": ALGORITHM_NAME,
                    "query_provider": provider_result.provider,
                    "query_model": provider_result.model,
                    "query_dimensions": provider_result.dimensions,
                    "memory_provider": candidate.memory.provider,
                    "memory_model": candidate.memory.model,
                    "vector_score": candidate.vector_score,
                },
            )
            for rank, candidate in enumerate(candidates, start=1)
        ]

        if not evidence:
            return []

        return self.evidence_repository.upsert_all(evidence)

    def list_evidence(self) -> list[Evidence]:
        return self.evidence_repository.list_all()


def _fingerprint(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _stable_evidence_id(*, question_fingerprint: str, memory_id: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{question_fingerprint}:{memory_id}"))
