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
    await client.post(f"/sources/{source_id}/content")
    await client.post(f"/sources/{source_id}/content/chunks")
    await client.post(f"/sources/{source_id}/content/chunks/memory")


@pytest.mark.anyio
async def test_constructs_answer_from_evidence(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text="AWS Lambda was required for this backend opportunity.",
        )

        response = await client.post(
            "/answers",
            json={"question": "Which opportunities required AWS Lambda?"},
        )

    assert response.status_code == 201
    answer = response.json()
    assert answer["question"] == "Which opportunities required AWS Lambda?"
    assert "AWS Lambda was required for this backend opportunity." in answer["text"]
    assert len(answer["evidence_ids"]) == 1
    assert answer["provider"] == "trampomemo-local"
    assert answer["model"] == "trampomemo-local-answer-deterministic-v1"
    assert answer["provider_metadata"] == {
        "purpose": "development_and_test",
        "semantic_model": False,
    }
    assert answer["generation_metadata"]["evidence_count"] == 1


@pytest.mark.anyio
async def test_lists_constructed_answers_for_review(test_session_factory, tmp_path: Path):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text="The recruiter mentioned remote work.",
        )
        created_response = await client.post(
            "/answers",
            json={"question": "Which recruiter mentioned remote work?"},
        )

        response = await client.get("/answers")

    assert response.status_code == 200
    assert response.json() == [created_response.json()]


@pytest.mark.anyio
async def test_answer_construction_is_idempotent_for_same_question_and_evidence(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text="The interview focused on system design.",
        )

        first_response = await client.post(
            "/answers",
            json={"question": "Which interview focused on system design?"},
        )
        second_response = await client.post(
            "/answers",
            json={"question": "Which interview focused on system design?"},
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json() == second_response.json()


@pytest.mark.anyio
async def test_constructs_new_answer_when_new_evidence_supports_existing_question(
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
            "/answers",
            json={"question": "Which opportunities required AWS Lambda?"},
        )

        await create_memory(
            client,
            text="AWS Lambda appeared in the second opportunity.",
        )
        second_response = await client.post(
            "/answers",
            json={"question": "Which opportunities required AWS Lambda?"},
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert len(first_response.json()["evidence_ids"]) == 1
    assert len(second_response.json()["evidence_ids"]) == 2
    assert "first opportunity" in second_response.json()["text"]
    assert "second opportunity" in second_response.json()["text"]


@pytest.mark.anyio
async def test_constructs_insufficient_evidence_answer_when_no_evidence_supports_question(
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
            "/answers",
            json={"question": "Which companies required AWS Lambda?"},
        )

    assert response.status_code == 201
    answer = response.json()
    assert answer["evidence_ids"] == []
    assert answer["text"] == "I do not have enough evidence to answer this question."
    assert answer["generation_metadata"]["evidence_count"] == 0


@pytest.mark.anyio
async def test_answer_response_uses_evidence_not_memory_as_context(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await create_memory(
            client,
            text="Docker and Kubernetes appeared in the company requirements.",
        )

        response = await client.post(
            "/answers",
            json={"question": "Which companies mentioned Docker and Kubernetes?"},
        )

    assert response.status_code == 201
    answer = response.json()
    assert "evidence_ids" in answer
    assert "memory_ids" not in answer
