from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from trampomemo.main import create_app
from trampomemo.sources.models import Base


def setup_app(test_session_factory, tmp_path: Path):
    Base.metadata.create_all(test_session_factory.engine)
    return create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )


async def create_source_content(
    client: AsyncClient,
    *,
    source_type: str = "personal_note",
    title: str = "Source",
    text: str,
):
    source_response = await client.post(
        "/sources",
        data={
            "source_type": source_type,
            "title": title,
            "text": text,
        },
    )
    source_id = source_response.json()["id"]
    content_response = await client.post(f"/sources/{source_id}/content")
    return source_id, content_response.json()["id"]


@pytest.mark.anyio
async def test_creates_reviewable_chunks_from_source_content(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, content_id = await create_source_content(
            client,
            text="AWS Lambda was required.\n\nDocker was mentioned in the interview.",
        )

        response = await client.post(f"/sources/{source_id}/content/chunks")

    assert response.status_code == 201
    chunks = response.json()
    assert [chunk["sequence"] for chunk in chunks] == [1]
    assert chunks[0]["source_id"] == source_id
    assert chunks[0]["source_content_id"] == content_id
    assert chunks[0]["text"] == "AWS Lambda was required.\n\nDocker was mentioned in the interview."
    assert chunks[0]["start_char"] == 0
    assert chunks[0]["end_char"] == 64
    assert chunks[0]["character_count"] == 64
    assert chunks[0]["heading_path"] == []


@pytest.mark.anyio
async def test_returns_chunks_in_source_order(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, _ = await create_source_content(
            client,
            text="First note about English.\n\nSecond note about remote work.",
        )
        await client.post(f"/sources/{source_id}/content/chunks")

        response = await client.get(f"/sources/{source_id}/content/chunks")

    assert response.status_code == 200
    chunks = response.json()
    assert [chunk["sequence"] for chunk in chunks] == [1]
    assert chunks[0]["text"] == "First note about English.\n\nSecond note about remote work."


@pytest.mark.anyio
async def test_preserves_markdown_heading_path(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, _ = await create_source_content(
            client,
            source_type="markdown",
            title="Interview feedback",
            text=(
                "# Interview Feedback\n\n"
                "## Architecture\n\n"
                "Kafka and RabbitMQ were discussed.\n\n"
                "## English\n\n"
                "The interview was in English."
            ),
        )

        response = await client.post(f"/sources/{source_id}/content/chunks")

    assert response.status_code == 201
    chunks = response.json()
    assert [chunk["heading_path"] for chunk in chunks] == [
        ["Interview Feedback", "Architecture"],
        ["Interview Feedback", "English"],
    ]
    assert chunks[0]["text"] == "## Architecture\n\nKafka and RabbitMQ were discussed."
    assert chunks[1]["text"] == "## English\n\nThe interview was in English."


@pytest.mark.anyio
async def test_splits_oversized_content_without_rewriting_it(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)
    paragraph_one = "AWS Lambda was required. " * 35
    paragraph_two = "Kubernetes was mentioned. " * 35

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, _ = await create_source_content(
            client,
            text=f"{paragraph_one.strip()}\n\n{paragraph_two.strip()}",
        )

        response = await client.post(f"/sources/{source_id}/content/chunks")

    assert response.status_code == 201
    chunks = response.json()
    assert len(chunks) == 2
    assert chunks[0]["sequence"] == 1
    assert chunks[1]["sequence"] == 2
    assert chunks[0]["text"] == paragraph_one.strip()
    assert chunks[1]["text"] == paragraph_two.strip()
    assert chunks[0]["end_char"] < chunks[1]["start_char"]


@pytest.mark.anyio
async def test_chunk_generation_is_deterministic(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, _ = await create_source_content(
            client,
            text="The company uses SQS.\n\nThe recruiter mentioned remote work.",
        )

        first_response = await client.post(f"/sources/{source_id}/content/chunks")
        second_response = await client.post(f"/sources/{source_id}/content/chunks")

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    first_chunks = first_response.json()
    second_chunks = second_response.json()
    assert first_chunks == second_chunks


@pytest.mark.anyio
async def test_refuses_to_chunk_failed_source_content(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, _ = await create_source_content(client, text=" \n\n ")

        response = await client.post(f"/sources/{source_id}/content/chunks")

    assert response.status_code == 409
    assert response.json()["detail"] == "Only ready SourceContent can produce Chunks."
