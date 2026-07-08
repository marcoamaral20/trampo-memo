import math
import re
from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from trampomemo.chunks.models import Chunk
from trampomemo.memory.models import Memory

ALGORITHM_NAME = "deterministic_memory_search_v1"
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_STOP_WORDS = {
    "and",
    "are",
    "did",
    "for",
    "from",
    "has",
    "have",
    "the",
    "this",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "with",
}


@dataclass(frozen=True)
class MemorySearchResult:
    memory: Memory
    chunk: Chunk
    vector_score: float
    relevance_score: float


class MemoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_for_chunk(
        self,
        *,
        chunk_id: str,
        model: str,
        fingerprint: str,
    ) -> Memory | None:
        result = self.session.execute(
            select(Memory).where(
                Memory.chunk_id == chunk_id,
                Memory.model == model,
                Memory.fingerprint == fingerprint,
            )
        )
        return result.scalar_one_or_none()

    def list_by_source_id(self, source_id: str) -> list[Memory]:
        result = self.session.execute(
            select(Memory).where(Memory.source_id == source_id).order_by(Memory.created_at.asc())
        )
        return list(result.scalars())

    def list_all(self) -> list[Memory]:
        result = self.session.execute(select(Memory).order_by(Memory.created_at.asc()))
        return list(result.scalars())

    def search_relevant(
        self,
        *,
        question: str,
        query_vector: list[float],
        limit: int,
    ) -> list[MemorySearchResult]:
        if self.session.bind is not None and self.session.bind.dialect.name == "postgresql":
            return self._search_relevant_with_pgvector(
                question=question,
                query_vector=query_vector,
                limit=limit,
            )

        return self._search_relevant_in_python(
            question=question,
            query_vector=query_vector,
            limit=limit,
        )

    def save_all(self, memories: list[Memory]) -> list[Memory]:
        self.session.add_all(memories)
        self.session.commit()
        for memory in memories:
            self.session.refresh(memory)
        return memories

    def _search_relevant_with_pgvector(
        self,
        *,
        question: str,
        query_vector: list[float],
        limit: int,
    ) -> list[MemorySearchResult]:
        token_filters = {
            f"token_{index}": f"%{token}%" for index, token in enumerate(sorted(_tokens(question)))
        }
        if not token_filters:
            return []

        token_where = " OR ".join(f"chunks.text ILIKE :{name}" for name in token_filters)
        query_dimensions = len(query_vector)
        vector_type = _pgvector_type(query_dimensions)
        distance_expression = (
            f"CAST(memories.vector AS {vector_type}) <=> CAST(:query_vector AS {vector_type})"
        )
        query = text(
            f"""
            SELECT
                memories.id AS memory_id,
                chunks.id AS chunk_id,
                1 - ({distance_expression}) AS vector_score
            FROM memories
            JOIN chunks ON chunks.id = memories.chunk_id
            WHERE memories.dimensions = :query_dimensions AND ({token_where})
            ORDER BY {distance_expression}, chunks.sequence ASC
            LIMIT :limit
            """
        )
        params = {
            "query_vector": _vector_literal(query_vector),
            "query_dimensions": query_dimensions,
            "limit": limit,
            **token_filters,
        }
        rows = self.session.execute(query, params).mappings()
        results: list[MemorySearchResult] = []
        for row in rows:
            memory = self.session.get(Memory, row["memory_id"])
            chunk = self.session.get(Chunk, row["chunk_id"])
            if memory is None or chunk is None:
                continue
            vector_score = round(float(row["vector_score"]), 6)
            results.append(
                MemorySearchResult(
                    memory=memory,
                    chunk=chunk,
                    vector_score=vector_score,
                    relevance_score=vector_score,
                )
            )
        return results

    def _search_relevant_in_python(
        self,
        *,
        question: str,
        query_vector: list[float],
        limit: int,
    ) -> list[MemorySearchResult]:
        question_tokens = _tokens(question)
        memories = self.list_all()
        candidates: list[MemorySearchResult] = []

        for memory in memories:
            if memory.dimensions != len(query_vector):
                continue

            chunk = self.session.get(Chunk, memory.chunk_id)
            if chunk is None:
                continue

            token_overlap = _token_overlap(question_tokens, _tokens(chunk.text))
            if token_overlap == 0:
                continue

            vector_score = _cosine_similarity(query_vector, memory.vector)
            relevance_score = round((vector_score + token_overlap) / 2, 6)
            candidates.append(
                MemorySearchResult(
                    memory=memory,
                    chunk=chunk,
                    vector_score=round(vector_score, 6),
                    relevance_score=relevance_score,
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.relevance_score,
                candidate.vector_score,
                candidate.chunk.sequence * -1,
            ),
            reverse=True,
        )[:limit]


def _tokens(text_value: str) -> set[str]:
    return {
        token
        for token in _TOKEN_PATTERN.findall(text_value.lower())
        if len(token) > 2 and token not in _STOP_WORDS
    }


def _token_overlap(question_tokens: set[str], chunk_tokens: set[str]) -> float:
    if not question_tokens:
        return 0
    return len(question_tokens.intersection(chunk_tokens)) / len(question_tokens)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0

    dot_product = sum(
        left_value * right_value for left_value, right_value in zip(left, right, strict=True)
    )
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0
    return dot_product / (left_norm * right_norm)


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(item) for item in vector) + "]"


def _pgvector_type(dimensions: int) -> str:
    if dimensions <= 0:
        raise ValueError("Vector dimensions must be greater than zero.")
    return f"vector({dimensions})"
