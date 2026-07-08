from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from trampomemo.core.base import Base
from trampomemo.memory.vector_type import Vector


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[str] = mapped_column(
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    vector: Mapped[list[float]] = mapped_column(Vector(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    @property
    def vector_preview(self) -> list[float]:
        return self.vector[:3]
