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


async def create_memory(client: AsyncClient, *, text: str):
    source_response = await client.post(
        "/sources",
        data={
            "source_type": "job_description",
            "title": "Backend role",
            "text": text,
        },
    )
    source_id = source_response.json()["id"]
    content_response = await client.post(f"/sources/{source_id}/content")
    chunk_response = await client.post(f"/sources/{source_id}/content/chunks")
    memory_response = await client.post(f"/sources/{source_id}/content/chunks/memory")
    return (
        source_response.json(),
        content_response.json(),
        chunk_response.json(),
        memory_response.json(),
    )


@pytest.mark.anyio
async def test_constructs_evidence_from_memory_for_a_question(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source, content, chunks, memories = await create_memory(
            client,
            text="AWS Lambda was required for this role.\n\nThe recruiter mentioned English.",
        )

        response = await client.post(
            "/evidence",
            json={"question": "Which opportunities required AWS Lambda?"},
        )

    assert response.status_code == 201
    evidence = response.json()
    assert len(evidence) == 1
    assert evidence[0]["question"] == "Which opportunities required AWS Lambda?"
    assert evidence[0]["source_id"] == source["id"]
    assert evidence[0]["source_content_id"] == content["id"]
    assert evidence[0]["chunk_id"] == chunks[0]["id"]
    assert evidence[0]["memory_id"] == memories[0]["id"]
    assert "AWS Lambda was required for this role." in evidence[0]["excerpt"]
    assert evidence[0]["rank"] == 1
    assert evidence[0]["relevance_score"] > 0
    assert evidence[0]["trace_metadata"]["algorithm"] == "deterministic_memory_search_v1"
    assert evidence[0]["trace_metadata"]["query_provider"] == "trampomemo-local"


@pytest.mark.anyio
async def test_lists_constructed_evidence_for_engineering_review(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text=(
                "The interview focused on system design.\n\nDocker appeared in the job description."
            ),
        )
        created_response = await client.post(
            "/evidence",
            json={"question": "Which interview focused on system design?"},
        )

        response = await client.get("/evidence")

    assert response.status_code == 200
    assert response.json() == created_response.json()


@pytest.mark.anyio
async def test_evidence_construction_is_idempotent_for_the_same_question(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text="The company required Kubernetes experience.",
        )

        first_response = await client.post(
            "/evidence",
            json={"question": "Which companies required Kubernetes?"},
        )
        second_response = await client.post(
            "/evidence",
            json={"question": "Which companies required Kubernetes?"},
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json() == second_response.json()


@pytest.mark.anyio
async def test_reconstructs_evidence_when_new_memory_supports_existing_question(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text="AWS Lambda appeared in the first opportunity.",
        )
        first_response = await client.post(
            "/evidence",
            json={"question": "Which opportunities required AWS Lambda?"},
        )

        await create_memory(
            client,
            text="AWS Lambda appeared in the second opportunity.",
        )
        second_response = await client.post(
            "/evidence",
            json={"question": "Which opportunities required AWS Lambda?"},
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert len(first_response.json()) == 1
    assert len(second_response.json()) == 2
    assert {
        "AWS Lambda appeared in the first opportunity.",
        "AWS Lambda appeared in the second opportunity.",
    } == {item["excerpt"] for item in second_response.json()}


@pytest.mark.anyio
async def test_returns_empty_evidence_when_memory_does_not_support_the_question(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text="The process involved a portfolio review.",
        )

        response = await client.post(
            "/evidence",
            json={"question": "Which companies required AWS Lambda?"},
        )

    assert response.status_code == 201
    assert response.json() == []


@pytest.mark.anyio
async def test_returns_empty_evidence_when_memory_has_not_been_built(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/sources",
            data={
                "source_type": "personal_note",
                "title": "Unprepared note",
                "text": "AWS Lambda appeared here, but Memory was not built.",
            },
        )

        response = await client.post(
            "/evidence",
            json={"question": "Which notes mentioned AWS Lambda?"},
        )

    assert response.status_code == 201
    assert response.json() == []
