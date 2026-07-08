import pytest

from trampomemo.core.config import Settings
from trampomemo.core.provider_errors import ProviderConfigurationError
from trampomemo.memory.embedding_provider import (
    DeterministicLocalEmbeddingProvider,
    OpenAIEmbeddingProvider,
    create_embedding_provider,
)


def test_creates_local_embedding_provider_by_default() -> None:
    provider = create_embedding_provider(Settings())

    assert isinstance(provider, DeterministicLocalEmbeddingProvider)


def test_creates_openai_embedding_provider_from_settings() -> None:
    provider = create_embedding_provider(
        Settings(
            embedding_provider="openai",
            openai_api_key="sk-test",
        )
    )

    assert isinstance(provider, OpenAIEmbeddingProvider)
    assert provider.provider == "openai"
    assert provider.model == "text-embedding-3-small"
    assert provider.dimensions == 1536


def test_refuses_openai_embedding_provider_without_api_key() -> None:
    with pytest.raises(ProviderConfigurationError, match="OPENAI_API_KEY"):
        create_embedding_provider(Settings(embedding_provider="openai"))


def test_refuses_unknown_embedding_provider() -> None:
    with pytest.raises(ProviderConfigurationError, match="Unsupported embedding provider"):
        create_embedding_provider(Settings(embedding_provider="unknown"))


def test_openai_embedding_provider_returns_provider_result(monkeypatch) -> None:
    captured_payload = {}

    def fake_post_openai_json(*, url, api_key, payload, provider):
        captured_payload.update(
            {
                "url": url,
                "api_key": api_key,
                "payload": payload,
                "provider": provider,
            }
        )
        return {
            "data": [{"embedding": [0.1, 0.2, 0.3]}],
            "usage": {"total_tokens": 7},
        }

    monkeypatch.setattr(
        "trampomemo.memory.embedding_provider.post_openai_json",
        fake_post_openai_json,
    )
    provider = OpenAIEmbeddingProvider(
        api_key="sk-test",
        base_url="https://api.openai.com/v1",
        model="text-embedding-3-small",
        dimensions=1536,
    )

    result = provider.generate_vector(text="AWS Lambda")

    assert captured_payload["url"] == "https://api.openai.com/v1/embeddings"
    assert captured_payload["payload"] == {
        "model": "text-embedding-3-small",
        "input": "AWS Lambda",
        "dimensions": 1536,
    }
    assert result.vector == [0.1, 0.2, 0.3]
    assert result.dimensions == 3
    assert result.provider == "openai"
    assert result.metadata["usage"] == {"total_tokens": 7}
