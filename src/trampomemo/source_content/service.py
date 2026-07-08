from trampomemo.source_content.extractors import SourceExtractorRegistry
from trampomemo.source_content.models import SourceContent, SourceContentStatus
from trampomemo.source_content.repository import SourceContentRepository
from trampomemo.sources.models import SourceStatus
from trampomemo.sources.source_repository import SourceRepository
from trampomemo.sources.source_storage import SourceStorage


class SourceNotFoundError(Exception):
    pass


class SourceCannotProduceContentError(Exception):
    pass


class SourceContentNotFoundError(Exception):
    pass


class SourceContentService:
    def __init__(
        self,
        *,
        source_repository: SourceRepository,
        content_repository: SourceContentRepository,
        storage: SourceStorage,
        extractor_registry: SourceExtractorRegistry | None = None,
    ) -> None:
        self.source_repository = source_repository
        self.content_repository = content_repository
        self.storage = storage
        self.extractor_registry = extractor_registry or SourceExtractorRegistry()

    def create_source_content(self, *, source_id: str) -> SourceContent:
        source = self.source_repository.get(source_id)
        if source is None:
            raise SourceNotFoundError

        if source.status != SourceStatus.IMPORTED.value:
            raise SourceCannotProduceContentError

        extractor = self.extractor_registry.extractor_for(source)
        if extractor is None:
            return self._save_content(
                source_id=source.id,
                text="",
                status=SourceContentStatus.EXTRACTION_FAILED,
                failure_reason="unsupported_source_content",
            )

        result = extractor.extract(source=source, storage=self.storage)
        if result.failure_reason is not None:
            return self._save_content(
                source_id=source.id,
                text=result.text,
                status=SourceContentStatus.EXTRACTION_FAILED,
                failure_reason=result.failure_reason,
            )

        if result.text == "":
            return self._save_content(
                source_id=source.id,
                text="",
                status=SourceContentStatus.EXTRACTION_FAILED,
                failure_reason="empty_source_content",
            )

        return self._save_content(
            source_id=source.id,
            text=result.text,
            status=SourceContentStatus.READY_FOR_MEMORY,
            failure_reason=None,
        )

    def get_source_content(self, *, source_id: str) -> SourceContent:
        source_content = self.content_repository.get_by_source_id(source_id)
        if source_content is None:
            raise SourceContentNotFoundError

        return source_content

    def _save_content(
        self,
        *,
        source_id: str,
        text: str,
        status: SourceContentStatus,
        failure_reason: str | None,
    ) -> SourceContent:
        source_content = self.content_repository.get_by_source_id(source_id)
        if source_content is None:
            source_content = SourceContent(source_id=source_id)

        source_content.text = text
        source_content.status = status.value
        source_content.failure_reason = failure_reason
        source_content.character_count = len(text)

        source = self.source_repository.get(source_id)
        if source is None:
            raise SourceNotFoundError
        source.content_status = status.value

        self.source_repository.save(source)
        return self.content_repository.save(source_content)
