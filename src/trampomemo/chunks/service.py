from uuid import NAMESPACE_URL, uuid5

from trampomemo.chunks.chunker import build_chunk_candidates
from trampomemo.chunks.models import Chunk
from trampomemo.chunks.repository import ChunkRepository
from trampomemo.source_content.models import SourceContentStatus
from trampomemo.source_content.repository import SourceContentRepository
from trampomemo.source_content.service import (
    SourceContentNotFoundError,
    SourceNotFoundError,
)
from trampomemo.sources.source_repository import SourceRepository


class SourceContentCannotProduceChunksError(Exception):
    pass


class ChunkService:
    def __init__(
        self,
        *,
        source_repository: SourceRepository,
        content_repository: SourceContentRepository,
        chunk_repository: ChunkRepository,
    ) -> None:
        self.source_repository = source_repository
        self.content_repository = content_repository
        self.chunk_repository = chunk_repository

    def create_chunks(self, *, source_id: str) -> list[Chunk]:
        source = self.source_repository.get(source_id)
        if source is None:
            raise SourceNotFoundError

        source_content = self.content_repository.get_by_source_id(source_id)
        if source_content is None:
            raise SourceContentNotFoundError

        if source_content.status != SourceContentStatus.READY_FOR_MEMORY.value:
            raise SourceContentCannotProduceChunksError

        existing_chunks = self.chunk_repository.list_by_source_content_id(source_content.id)
        if existing_chunks:
            return existing_chunks

        candidates = build_chunk_candidates(source=source, text=source_content.text)
        chunks = [
            Chunk(
                id=_stable_chunk_id(
                    source_content_id=source_content.id,
                    sequence=candidate.sequence,
                    start_char=candidate.start_char,
                    end_char=candidate.end_char,
                    text=candidate.text,
                ),
                source_id=source.id,
                source_content_id=source_content.id,
                sequence=candidate.sequence,
                text=candidate.text,
                start_char=candidate.start_char,
                end_char=candidate.end_char,
                character_count=len(candidate.text),
                heading_path=candidate.heading_path,
            )
            for candidate in candidates
        ]
        return self.chunk_repository.replace_for_source_content(
            source_content_id=source_content.id,
            chunks=chunks,
        )

    def list_chunks(self, *, source_id: str) -> list[Chunk]:
        source = self.source_repository.get(source_id)
        if source is None:
            raise SourceNotFoundError

        source_content = self.content_repository.get_by_source_id(source_id)
        if source_content is None:
            raise SourceContentNotFoundError

        return self.chunk_repository.list_by_source_content_id(source_content.id)


def _stable_chunk_id(
    *,
    source_content_id: str,
    sequence: int,
    start_char: int,
    end_char: int,
    text: str,
) -> str:
    chunk_key = f"{source_content_id}:{sequence}:{start_char}:{end_char}:{text}"
    return str(uuid5(NAMESPACE_URL, chunk_key))
