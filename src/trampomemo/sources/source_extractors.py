from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from trampomemo.sources.models import Source, SourceOrigin
from trampomemo.sources.source_storage import SourceStorage
from trampomemo.sources.text_normalization import normalize_source_text


@dataclass(frozen=True)
class SourceExtractionResult:
    text: str
    failure_reason: str | None = None


class SourceExtractor:
    def extract(self, *, source: Source, storage: SourceStorage) -> SourceExtractionResult:
        raise NotImplementedError


class StoredTextExtractor(SourceExtractor):
    def extract(self, *, source: Source, storage: SourceStorage) -> SourceExtractionResult:
        if source.storage_uri is None:
            return SourceExtractionResult(text="", failure_reason="missing_source_content")

        return SourceExtractionResult(
            text=normalize_source_text(storage.read_text(storage_uri=source.storage_uri))
        )


class PlainTextFileExtractor(StoredTextExtractor):
    pass


class MarkdownFileExtractor(StoredTextExtractor):
    pass


class PdfFileExtractor(SourceExtractor):
    def extract(self, *, source: Source, storage: SourceStorage) -> SourceExtractionResult:
        if source.storage_uri is None:
            return SourceExtractionResult(text="", failure_reason="missing_source_content")

        try:
            reader = PdfReader(BytesIO(storage.read_bytes(storage_uri=source.storage_uri)))
            page_texts = [page.extract_text() or "" for page in reader.pages]
        except Exception:
            return SourceExtractionResult(text="", failure_reason="unreadable_pdf")

        return SourceExtractionResult(text=normalize_source_text("\n\n".join(page_texts)))


class SourceExtractorRegistry:
    def __init__(self) -> None:
        self.direct_text_extractor = StoredTextExtractor()
        self.file_extractors: dict[str, SourceExtractor] = {
            ".txt": PlainTextFileExtractor(),
            ".md": MarkdownFileExtractor(),
            ".markdown": MarkdownFileExtractor(),
            ".pdf": PdfFileExtractor(),
        }

    def extractor_for(self, source: Source) -> SourceExtractor | None:
        if source.source_origin == SourceOrigin.TEXT.value:
            return self.direct_text_extractor

        if source.source_origin != SourceOrigin.FILE.value or source.original_filename is None:
            return None

        extension = Path(source.original_filename).suffix.lower()
        return self.file_extractors.get(extension)
