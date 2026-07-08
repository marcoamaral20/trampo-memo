from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from trampomemo.core.base import Base


class SourceStatus(StrEnum):
    IMPORTED = "imported"
    IMPORT_FAILED = "import_failed"


class SourceContentStatus(StrEnum):
    NOT_STARTED = "not_started"
    READY_FOR_MEMORY = "ready_for_memory"
    EXTRACTION_FAILED = "extraction_failed"


class SourceOrigin(StrEnum):
    TEXT = "text"
    FILE = "file"


class SourceType(StrEnum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    COMPANY_INFORMATION = "company_information"
    RECRUITER_CONVERSATION = "recruiter_conversation"
    INTERVIEW_FEEDBACK = "interview_feedback"
    PERSONAL_NOTE = "personal_note"
    EMAIL = "email"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    PDF = "pdf"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_origin: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    origin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    content_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=SourceContentStatus.NOT_STARTED.value,
    )
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
