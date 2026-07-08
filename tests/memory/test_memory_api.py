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


async def create_chunks(client: AsyncClient, *, text: str):
    source_response = await client.post(
        "/sources",
        data={
            "source_type": "personal_note",
            "title": "Memory source",
            "text": text,
        },
    )
    source_id = source_response.json()["id"]
    await client.post(f"/sources/{source_id}/content")
    chunk_response = await client.post(f"/sources/{source_id}/content/chunks")
    return source_id, chunk_response.json()


@pytest.mark.anyio
async def test_builds_reviewable_memory_from_chunks(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, chunks = await create_chunks(
            client,
            text="AWS Lambda was required.\n\nDocker was mentioned.",
        )

        response = await client.post(f"/sources/{source_id}/content/chunks/memory")

    assert response.status_code == 201
    memories = response.json()
    assert len(memories) == len(chunks)
    assert memories[0]["source_id"] == source_id
    assert memories[0]["chunk_id"] == chunks[0]["id"]
    assert memories[0]["provider"] == "trampomemo-local"
    assert memories[0]["model"] == "trampomemo-local-deterministic-v1"
    assert memories[0]["dimensions"] == 8
    assert memories[0]["fingerprint"]
    assert memories[0]["provider_metadata"] == {
        "purpose": "development_and_test",
        "semantic_model": False,
    }
    assert len(memories[0]["vector_preview"]) == 3


@pytest.mark.anyio
async def test_lists_memory_for_source_chunks(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, chunks = await create_chunks(
            client,
            text="The recruiter mentioned English.\n\nThe role is remote.",
        )
        await client.post(f"/sources/{source_id}/content/chunks/memory")

        response = await client.get(f"/sources/{source_id}/content/chunks/memory")

    assert response.status_code == 200
    memories = response.json()
    assert [memory["chunk_id"] for memory in memories] == [chunk["id"] for chunk in chunks]


@pytest.mark.anyio
async def test_memory_construction_is_idempotent(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_id, _ = await create_chunks(
            client,
            text="Kafka appeared in one interview.\n\nSQS appeared in another.",
        )

        first_response = await client.post(f"/sources/{source_id}/content/chunks/memory")
        second_response = await client.post(f"/sources/{source_id}/content/chunks/memory")

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json() == second_response.json()


@pytest.mark.anyio
async def test_refuses_to_build_memory_without_chunks(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await client.post(
            "/sources",
            data={
                "source_type": "personal_note",
                "title": "Unchunked source",
                "text": "This has content but no chunks yet.",
            },
        )
        source_id = source_response.json()["id"]
        await client.post(f"/sources/{source_id}/content")

        response = await client.post(f"/sources/{source_id}/content/chunks/memory")

    assert response.status_code == 409
    assert response.json()["detail"] == "Chunks must exist before Memory can be built."
