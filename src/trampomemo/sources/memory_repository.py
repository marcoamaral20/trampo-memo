from sqlalchemy import select
from sqlalchemy.orm import Session

from trampomemo.sources.models import Memory


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

    def save_all(self, memories: list[Memory]) -> list[Memory]:
        self.session.add_all(memories)
        self.session.commit()
        for memory in memories:
            self.session.refresh(memory)
        return memories
