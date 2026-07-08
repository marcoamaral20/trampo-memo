from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from trampomemo.core.models import Base
from trampomemo.main import create_app


def setup_app(test_session_factory, tmp_path: Path):
    Base.metadata.create_all(test_session_factory.engine)
    return create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )


async def create_text_source(client: AsyncClient, *, text: str):
    return await client.post(
        "/sources",
        data={
            "source_type": "personal_note",
            "title": "System design prep",
            "text": text,
        },
    )


def create_pdf_bytes(text: str) -> bytes:
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET\n".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n%sendstream" % (len(content), content),
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for index, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode())
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return bytes(pdf)


@pytest.mark.anyio
async def test_creates_reviewable_content_from_text_source(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await create_text_source(
            client,
            text="  I answered a Kafka question.\r\n\r\n\r\nIt was about retries.  ",
        )
        source_id = source_response.json()["id"]

        response = await client.post(f"/sources/{source_id}/content")

    assert response.status_code == 201
    body = response.json()
    assert body["source_id"] == source_id
    assert body["status"] == "ready_for_memory"
    assert body["text"] == "I answered a Kafka question.\n\nIt was about retries."
    assert body["character_count"] == 51
    assert body["failure_reason"] is None


@pytest.mark.anyio
async def test_returns_reviewable_content_for_source(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await create_text_source(
            client,
            text="The role requires AWS Lambda.",
        )
        source_id = source_response.json()["id"]
        await client.post(f"/sources/{source_id}/content")

        response = await client.get(f"/sources/{source_id}/content")

    assert response.status_code == 200
    body = response.json()
    assert body["source_id"] == source_id
    assert body["status"] == "ready_for_memory"
    assert body["text"] == "The role requires AWS Lambda."


@pytest.mark.anyio
async def test_source_list_shows_content_status(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await create_text_source(
            client,
            text="This interview focused on architecture.",
        )
        source_id = source_response.json()["id"]

        before_response = await client.get("/sources")
        await client.post(f"/sources/{source_id}/content")
        after_response = await client.get("/sources")

    assert before_response.json()[0]["content_status"] == "not_started"
    assert after_response.json()[0]["content_status"] == "ready_for_memory"


@pytest.mark.anyio
async def test_marks_empty_text_source_as_extraction_failed(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await create_text_source(client, text=" \n\n\t ")
        source_id = source_response.json()["id"]

        response = await client.post(f"/sources/{source_id}/content")

    assert response.status_code == 201
    body = response.json()
    assert body["source_id"] == source_id
    assert body["status"] == "extraction_failed"
    assert body["text"] == ""
    assert body["character_count"] == 0
    assert body["failure_reason"] == "empty_source_content"


@pytest.mark.anyio
async def test_does_not_extract_content_from_import_failed_source(
    test_session_factory, tmp_path: Path
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await client.post(
            "/sources",
            data={
                "source_type": "resume",
                "title": "Unsupported resume",
            },
            files={"file": ("resume.docx", b"not supported yet", "application/vnd.openxmlformats")},
        )
        source_id = source_response.json()["id"]

        response = await client.post(f"/sources/{source_id}/content")

    assert response.status_code == 409
    assert response.json()["detail"] == "Only imported Sources can produce SourceContent."


@pytest.mark.anyio
async def test_creates_reviewable_content_from_plain_text_file(
    test_session_factory, tmp_path: Path
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await client.post(
            "/sources",
            data={
                "source_type": "plain_text",
                "title": "Recruiter notes",
            },
            files={"file": ("notes.txt", b" Remote role\r\n\r\nEnglish required. ", "text/plain")},
        )
        source_id = source_response.json()["id"]

        response = await client.post(f"/sources/{source_id}/content")

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready_for_memory"
    assert body["text"] == "Remote role\n\nEnglish required."


@pytest.mark.anyio
async def test_creates_reviewable_content_from_markdown_file(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await client.post(
            "/sources",
            data={
                "source_type": "markdown",
                "title": "Interview feedback",
            },
            files={
                "file": (
                    "feedback.md",
                    b"# Architecture\n\n\nKafka and RabbitMQ were discussed.",
                    "text/markdown",
                )
            },
        )
        source_id = source_response.json()["id"]

        response = await client.post(f"/sources/{source_id}/content")

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready_for_memory"
    assert body["text"] == "# Architecture\n\nKafka and RabbitMQ were discussed."


@pytest.mark.anyio
async def test_creates_reviewable_content_from_pdf_file(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await client.post(
            "/sources",
            data={
                "source_type": "pdf",
                "title": "Company PDF",
            },
            files={
                "file": (
                    "company.pdf",
                    create_pdf_bytes("AWS Lambda and Docker"),
                    "application/pdf",
                )
            },
        )
        source_id = source_response.json()["id"]

        response = await client.post(f"/sources/{source_id}/content")

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready_for_memory"
    assert body["text"] == "AWS Lambda and Docker"
