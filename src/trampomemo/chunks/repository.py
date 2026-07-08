from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from trampomemo.chunks.models import Chunk


class ChunkRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_source_content_id(self, source_content_id: str) -> list[Chunk]:
        result = self.session.execute(
            select(Chunk)
            .where(Chunk.source_content_id == source_content_id)
            .order_by(Chunk.sequence.asc())
        )
        return list(result.scalars())

    def list_by_source_id(self, source_id: str) -> list[Chunk]:
        result = self.session.execute(
            select(Chunk).where(Chunk.source_id == source_id).order_by(Chunk.sequence.asc())
        )
        return list(result.scalars())

    def get(self, chunk_id: str) -> Chunk | None:
        result = self.session.execute(select(Chunk).where(Chunk.id == chunk_id))
        return result.scalar_one_or_none()

    def replace_for_source_content(
        self, *, source_content_id: str, chunks: list[Chunk]
    ) -> list[Chunk]:
        self.session.execute(delete(Chunk).where(Chunk.source_content_id == source_content_id))
        self.session.add_all(chunks)
        self.session.commit()
        for chunk in chunks:
            self.session.refresh(chunk)
        return chunks
