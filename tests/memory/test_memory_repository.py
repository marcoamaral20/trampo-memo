from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from trampomemo.core.models import Base
from trampomemo.main import create_app
from trampomemo.memory.embedding_provider import DeterministicLocalEmbeddingProvider
from trampomemo.memory.repository import MemoryRepository


def setup_app(test_session_factory, tmp_path: Path):
    Base.metadata.create_all(test_session_factory.engine)
    return create_app(
        session_factory=test_session_factory,
        source_storage_path=tmp_path / "sources",
    )


@pytest.mark.anyio
async def test_memory_repository_searches_relevant_memory(
    test_session_factory,
    tmp_path: Path,
):
    app = setup_app(test_session_factory, tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        source_response = await client.post(
            "/sources",
            data={
                "source_type": "job_description",
                "title": "Backend role",
                "text": "AWS Lambda was required.\n\nThe process involved a portfolio review.",
            },
        )
        source_id = source_response.json()["id"]
        await client.post(f"/sources/{source_id}/content")
        await client.post(f"/sources/{source_id}/content/chunks")
        await client.post(f"/sources/{source_id}/content/chunks/memory")

    provider_result = DeterministicLocalEmbeddingProvider().generate_vector(
        text="Which opportunities required AWS Lambda?"
    )

    with next(test_session_factory()) as session:
        results = MemoryRepository(session).search_relevant(
            question="Which opportunities required AWS Lambda?",
            query_vector=provider_result.vector,
            limit=3,
        )

    assert len(results) == 1
    assert "AWS Lambda was required." in results[0].chunk.text
    assert results[0].relevance_score > 0
    assert results[0].vector_score > 0
