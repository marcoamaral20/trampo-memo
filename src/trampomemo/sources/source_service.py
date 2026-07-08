from dataclasses import dataclass
from pathlib import Path

from trampomemo.sources.models import Source, SourceOrigin, SourceStatus, SourceType
from trampomemo.sources.source_repository import SourceRepository
from trampomemo.sources.source_storage import SourceStorage

SUPPORTED_FILE_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt"}


@dataclass(frozen=True)
class FileInput:
    filename: str
    content_type: str | None
    content: bytes


class SourceService:
    def __init__(self, *, repository: SourceRepository, storage: SourceStorage) -> None:
        self.repository = repository
        self.storage = storage

    def create_source(
        self,
        *,
        source_type: SourceType,
        title: str,
        origin: str | None,
        text: str | None,
        file: FileInput | None,
    ) -> Source:
        if not text and file is None:
            raise ValueError("A Source must include text or a file.")

        if file is not None:
            return self._create_file_source(
                source_type=source_type,
                title=title,
                origin=origin,
                file=file,
            )

        storage_uri = self.storage.save_text(content=text or "")
        return self.repository.add(
            Source(
                source_type=source_type.value,
                source_origin=SourceOrigin.TEXT.value,
                title=title,
                origin=origin,
                storage_uri=storage_uri,
                status=SourceStatus.IMPORTED.value,
            )
        )

    def list_sources(self) -> list[Source]:
        return self.repository.list()

    def _create_file_source(
        self,
        *,
        source_type: SourceType,
        title: str,
        origin: str | None,
        file: FileInput,
    ) -> Source:
        extension = Path(file.filename).suffix.lower()
        if extension not in SUPPORTED_FILE_EXTENSIONS:
            return self.repository.add(
                Source(
                    source_type=source_type.value,
                    source_origin=SourceOrigin.FILE.value,
                    title=title,
                    origin=origin,
                    original_filename=file.filename,
                    content_type=file.content_type,
                    status=SourceStatus.IMPORT_FAILED.value,
                    failure_reason="unsupported_file_type",
                )
            )

        storage_uri = self.storage.save_bytes(
            original_filename=file.filename,
            content=file.content,
        )
        return self.repository.add(
            Source(
                source_type=source_type.value,
                source_origin=SourceOrigin.FILE.value,
                title=title,
                origin=origin,
                original_filename=file.filename,
                content_type=file.content_type,
                storage_uri=storage_uri,
                status=SourceStatus.IMPORTED.value,
            )
        )
