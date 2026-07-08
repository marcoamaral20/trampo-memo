from sqlalchemy import select
from sqlalchemy.orm import Session

from trampomemo.sources.models import Evidence


class EvidenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Evidence]:
        result = self.session.execute(select(Evidence).order_by(Evidence.created_at.asc()))
        return list(result.scalars())

    def get_for_question_and_memory(
        self,
        *,
        question_fingerprint: str,
        memory_id: str,
    ) -> Evidence | None:
        result = self.session.execute(
            select(Evidence).where(
                Evidence.question_fingerprint == question_fingerprint,
                Evidence.memory_id == memory_id,
            )
        )
        return result.scalar_one_or_none()

    def upsert_all(self, evidence: list[Evidence]) -> list[Evidence]:
        result: list[Evidence] = []
        changed: list[Evidence] = []

        for item in evidence:
            existing = self.get_for_question_and_memory(
                question_fingerprint=item.question_fingerprint,
                memory_id=item.memory_id,
            )
            if existing is None:
                self.session.add(item)
                result.append(item)
                changed.append(item)
                continue

            if _has_evidence_changes(existing=existing, candidate=item):
                existing.question = item.question
                existing.source_id = item.source_id
                existing.source_content_id = item.source_content_id
                existing.chunk_id = item.chunk_id
                existing.excerpt = item.excerpt
                existing.rank = item.rank
                existing.relevance_score = item.relevance_score
                existing.trace_metadata = item.trace_metadata
                changed.append(existing)

            result.append(existing)

        if changed:
            self.session.commit()
            for item in changed:
                self.session.refresh(item)

        return sorted(result, key=lambda item: item.rank)


def _has_evidence_changes(*, existing: Evidence, candidate: Evidence) -> bool:
    return any(
        [
            existing.question != candidate.question,
            existing.source_id != candidate.source_id,
            existing.source_content_id != candidate.source_content_id,
            existing.chunk_id != candidate.chunk_id,
            existing.excerpt != candidate.excerpt,
            existing.rank != candidate.rank,
            existing.relevance_score != candidate.relevance_score,
            existing.trace_metadata != candidate.trace_metadata,
        ]
    )
