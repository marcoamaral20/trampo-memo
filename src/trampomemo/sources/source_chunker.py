import re
from dataclasses import dataclass

from trampomemo.sources.models import Source, SourceType

MAX_CHUNK_CHARS = 1000


@dataclass(frozen=True)
class ChunkCandidate:
    sequence: int
    text: str
    start_char: int
    end_char: int
    heading_path: list[str]


@dataclass(frozen=True)
class TextBlock:
    text: str
    start_char: int
    end_char: int
    heading_path: list[str]


def build_chunk_candidates(*, source: Source, text: str) -> list[ChunkCandidate]:
    blocks = _markdown_blocks(text) if _is_markdown_source(source) else _paragraph_blocks(text)
    chunks = _pack_blocks(blocks)
    return [
        ChunkCandidate(
            sequence=index,
            text=chunk.text,
            start_char=chunk.start_char,
            end_char=chunk.end_char,
            heading_path=chunk.heading_path,
        )
        for index, chunk in enumerate(chunks, start=1)
    ]


def _is_markdown_source(source: Source) -> bool:
    if source.source_type == SourceType.MARKDOWN.value:
        return True

    if source.original_filename is None:
        return False

    return source.original_filename.lower().endswith((".md", ".markdown"))


def _pack_blocks(blocks: list[TextBlock]) -> list[TextBlock]:
    packed: list[TextBlock] = []
    current: TextBlock | None = None

    for block in blocks:
        if len(block.text) > MAX_CHUNK_CHARS:
            if current is not None:
                packed.append(current)
                current = None
            packed.extend(_split_oversized_block(block))
            continue

        if current is None:
            current = block
            continue

        same_context = current.heading_path == block.heading_path
        combined_text = f"{current.text}\n\n{block.text}"
        combined_size = block.end_char - current.start_char
        if same_context and combined_size <= MAX_CHUNK_CHARS:
            current = TextBlock(
                text=combined_text,
                start_char=current.start_char,
                end_char=block.end_char,
                heading_path=current.heading_path,
            )
            continue

        packed.append(current)
        current = block

    if current is not None:
        packed.append(current)

    return packed


def _paragraph_blocks(text: str) -> list[TextBlock]:
    return [
        TextBlock(
            text=match.group(0),
            start_char=match.start(),
            end_char=match.end(),
            heading_path=[],
        )
        for match in _paragraph_matches(text)
    ]


def _markdown_blocks(text: str) -> list[TextBlock]:
    lines = text.splitlines(keepends=True)
    headings: list[str | None] = []
    blocks: list[TextBlock] = []
    section_start: int | None = None
    section_end = 0
    section_heading_path: list[str] = []
    section_has_body = False
    position = 0

    for line in lines:
        line_start = position
        line_end = position + len(line)
        stripped = line.strip()
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)

        if heading_match:
            if section_start is not None and section_has_body:
                blocks.append(
                    TextBlock(
                        text=text[section_start:section_end].strip(),
                        start_char=section_start,
                        end_char=section_end,
                        heading_path=section_heading_path,
                    )
                )

            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            headings = headings[: level - 1]
            while len(headings) < level - 1:
                headings.append(None)
            headings.append(title)

            current_path = [heading for heading in headings if heading is not None]
            section_start = line_start
            section_end = line_end
            section_heading_path = current_path
            section_has_body = False
            position = line_end
            continue

        if section_start is not None and stripped:
            section_end = line_end
            section_has_body = True

        position = line_end

    if section_start is not None and section_has_body:
        blocks.append(
            TextBlock(
                text=text[section_start:section_end].strip(),
                start_char=section_start,
                end_char=section_end,
                heading_path=section_heading_path,
            )
        )

    if blocks:
        return [block for block in blocks if block.text]

    return _paragraph_blocks(text)


def _split_oversized_block(block: TextBlock) -> list[TextBlock]:
    splits: list[TextBlock] = []
    for match in _sentence_group_matches(block.text):
        text = match.group(0).strip()
        if not text:
            continue
        start = block.start_char + match.start()
        end = block.start_char + match.end()
        splits.append(
            TextBlock(
                text=text,
                start_char=start,
                end_char=end,
                heading_path=block.heading_path,
            )
        )

    if not splits:
        return [block]

    return _pack_blocks(splits)


def _paragraph_matches(text: str):
    return re.finditer(r"\S(?:.*?)(?=\n\s*\n|\Z)", text, flags=re.DOTALL)


def _sentence_group_matches(text: str):
    return re.finditer(r".{1,1000}(?:[.!?](?=\s)|\Z)", text, flags=re.DOTALL)
