from hashlib import sha256
from uuid import NAMESPACE_URL, uuid5

from trampomemo.sources.chunk_repository import ChunkRepository
from trampomemo.sources.embedding_provider import (
    DeterministicLocalEmbeddingProvider,
    EmbeddingProvider,
)
from trampomemo.sources.memory_repository import MemoryRepository
from trampomemo.sources.models import Memory
from trampomemo.sources.source_content_service import SourceNotFoundError
from trampomemo.sources.source_repository import SourceRepository


class ChunksRequiredForMemoryError(Exception):
    pass


class MemoryBuilder:
    def __init__(
        self,
        *,
        source_repository: SourceRepository,
        chunk_repository: ChunkRepository,
        memory_repository: MemoryRepository,
        provider: EmbeddingProvider | None = None,
    ) -> None:
        self.source_repository = source_repository
        self.chunk_repository = chunk_repository
        self.memory_repository = memory_repository
        self.provider = provider or DeterministicLocalEmbeddingProvider()

    def build_memory(self, *, source_id: str) -> list[Memory]:
        source = self.source_repository.get(source_id)
        if source is None:
            raise SourceNotFoundError

        chunks = self.chunk_repository.list_by_source_id(source_id)
        if not chunks:
            raise ChunksRequiredForMemoryError

        memories: list[Memory] = []
        new_memories: list[Memory] = []
        for chunk in chunks:
            provider_result = self.provider.generate_vector(text=chunk.text)
            fingerprint = _fingerprint(chunk.text)
            existing = self.memory_repository.get_for_chunk(
                chunk_id=chunk.id,
                model=provider_result.model,
                fingerprint=fingerprint,
            )
            if existing is not None:
                memories.append(existing)
                continue

            memory = Memory(
                id=_stable_memory_id(
                    chunk_id=chunk.id,
                    model=provider_result.model,
                    fingerprint=fingerprint,
                ),
                source_id=chunk.source_id,
                chunk_id=chunk.id,
                model=provider_result.model,
                dimensions=provider_result.dimensions,
                provider=provider_result.provider,
                fingerprint=fingerprint,
                provider_metadata=provider_result.metadata,
                vector=provider_result.vector,
            )
            new_memories.append(memory)
            memories.append(memory)

        if new_memories:
            self.memory_repository.save_all(new_memories)

        return self.memory_repository.list_by_source_id(source_id)

    def list_memory(self, *, source_id: str) -> list[Memory]:
        source = self.source_repository.get(source_id)
        if source is None:
            raise SourceNotFoundError

        return self.memory_repository.list_by_source_id(source_id)


def _fingerprint(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _stable_memory_id(*, chunk_id: str, model: str, fingerprint: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{chunk_id}:{model}:{fingerprint}"))
