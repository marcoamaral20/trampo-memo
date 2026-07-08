from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from trampomemo.core.models import Base
from trampomemo.main import create_app


@pytest.mark.anyio
@pytest.mark.parametrize(
    "source_type",
    [
        "resume",
        "job_description",
        "company_information",
        "recruiter_conversation",
        "interview_feedback",
        "personal_note",
        "email",
        "markdown",
        "plain_text",
        "pdf",
    ],
)
async def test_creates_supported_source_types_from_text(
    source_type: str,
    test_session_factory,
    tmp_path: Path,
):
    Base.metadata.create_all(test_session_factory.engine)
    app = create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/sources",
            data={
                "source_type": source_type,
                "title": f"{source_type} source",
                "text": "Source content provided directly by the user.",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["source_type"] == source_type
    assert body["status"] == "imported"
    assert body["source_origin"] == "text"


@pytest.mark.anyio
async def test_creates_text_source_with_preserved_identity(test_session_factory, tmp_path: Path):
    Base.metadata.create_all(test_session_factory.engine)
    app = create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/sources",
            data={
                "source_type": "job_description",
                "title": "Backend Engineer at Acme",
                "origin": "LinkedIn",
                "text": "We use AWS Lambda and Docker.",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["source_type"] == "job_description"
    assert body["title"] == "Backend Engineer at Acme"
    assert body["origin"] == "LinkedIn"
    assert body["source_origin"] == "text"
    assert body["status"] == "imported"
    assert body["failure_reason"] is None
    assert body["original_filename"] is None
    assert body["storage_uri"].startswith("local://sources/")


@pytest.mark.anyio
async def test_creates_file_source_with_original_filename(test_session_factory, tmp_path: Path):
    Base.metadata.create_all(test_session_factory.engine)
    app = create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/sources",
            data={
                "source_type": "resume",
                "title": "Main resume",
                "origin": "local",
            },
            files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["source_type"] == "resume"
    assert body["title"] == "Main resume"
    assert body["source_origin"] == "file"
    assert body["status"] == "imported"
    assert body["original_filename"] == "resume.pdf"
    assert body["content_type"] == "application/pdf"
    assert body["storage_uri"].startswith("local://sources/")


@pytest.mark.anyio
async def test_lists_sources_with_status(test_session_factory, tmp_path: Path):
    Base.metadata.create_all(test_session_factory.engine)
    app = create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/sources",
            data={
                "source_type": "personal_note",
                "title": "System design prep",
                "text": "I answered a question about queues.",
            },
        )
        await client.post(
            "/sources",
            data={
                "source_type": "email",
                "title": "Recruiter email",
                "origin": "copied email",
                "text": "The role is remote.",
            },
        )

        response = await client.get("/sources")

    assert response.status_code == 200
    items = response.json()
    assert [item["title"] for item in items] == ["System design prep", "Recruiter email"]
    assert [item["status"] for item in items] == ["imported", "imported"]


@pytest.mark.anyio
async def test_records_failed_source_for_unsupported_file_type(
    test_session_factory, tmp_path: Path
):
    Base.metadata.create_all(test_session_factory.engine)
    app = create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/sources",
            data={
                "source_type": "resume",
                "title": "Unsupported resume",
                "origin": "local",
            },
            files={"file": ("resume.docx", b"not supported yet", "application/vnd.openxmlformats")},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["source_origin"] == "file"
    assert body["status"] == "import_failed"
    assert body["failure_reason"] == "unsupported_file_type"
    assert body["storage_uri"] is None
    assert body["original_filename"] == "resume.docx"


@pytest.mark.anyio
async def test_rejects_source_without_text_or_file(test_session_factory, tmp_path: Path):
    Base.metadata.create_all(test_session_factory.engine)
    app = create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/sources",
            data={
                "source_type": "company_information",
                "title": "Acme",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "A Source must include text or a file."
