import math
import re
from dataclasses import dataclass

from trampomemo.sources.models import Chunk, Memory

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
class MemorySearchCandidate:
    memory: Memory
    chunk: Chunk
    vector_score: float
    token_overlap: float
    relevance_score: float


class DeterministicMemorySearch:
    def search(
        self,
        *,
        question: str,
        question_vector: list[float],
        memories: list[Memory],
        chunks_by_id: dict[str, Chunk],
        limit: int,
    ) -> list[MemorySearchCandidate]:
        question_tokens = _tokens(question)
        candidates: list[MemorySearchCandidate] = []

        for memory in memories:
            chunk = chunks_by_id.get(memory.chunk_id)
            if chunk is None:
                continue

            token_overlap = _token_overlap(question_tokens, _tokens(chunk.text))
            if token_overlap == 0:
                continue

            vector_score = _cosine_similarity(question_vector, memory.vector)
            relevance_score = round((vector_score + token_overlap) / 2, 6)
            candidates.append(
                MemorySearchCandidate(
                    memory=memory,
                    chunk=chunk,
                    vector_score=round(vector_score, 6),
                    token_overlap=round(token_overlap, 6),
                    relevance_score=relevance_score,
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.relevance_score,
                candidate.token_overlap,
                candidate.vector_score,
                candidate.chunk.sequence * -1,
            ),
            reverse=True,
        )[:limit]


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in _TOKEN_PATTERN.findall(text.lower())
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
