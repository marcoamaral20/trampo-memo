from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from trampomemo.core.config import Settings
from trampomemo.core.openai_http import post_openai_json
from trampomemo.core.provider_errors import ProviderConfigurationError


@dataclass(frozen=True)
class ProviderResult:
    vector: list[float]
    model: str
    dimensions: int
    provider: str
    metadata: dict


class EmbeddingProvider(Protocol):
    def generate_vector(self, *, text: str) -> ProviderResult:
        raise NotImplementedError


class DeterministicLocalEmbeddingProvider:
    provider = "trampomemo-local"
    model = "trampomemo-local-deterministic-v1"
    dimensions = 8

    def generate_vector(self, *, text: str) -> ProviderResult:
        digest = sha256(text.encode("utf-8")).digest()
        vector = [
            round(int.from_bytes(digest[index : index + 4], "big") / 2**32, 8)
            for index in range(0, self.dimensions * 4, 4)
        ]
        return ProviderResult(
            vector=vector,
            model=self.model,
            dimensions=self.dimensions,
            provider=self.provider,
            metadata={
                "purpose": "development_and_test",
                "semantic_model": False,
            },
        )


class OpenAIEmbeddingProvider:
    provider = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        dimensions: int,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.dimensions = dimensions

    def generate_vector(self, *, text: str) -> ProviderResult:
        response = post_openai_json(
            url=f"{self.base_url}/embeddings",
            api_key=self.api_key,
            payload={
                "model": self.model,
                "input": text,
                "dimensions": self.dimensions,
            },
            provider=self.provider,
        )
        embedding = response["data"][0]["embedding"]
        return ProviderResult(
            vector=embedding,
            model=self.model,
            dimensions=len(embedding),
            provider=self.provider,
            metadata={
                "usage": response.get("usage", {}),
                "configured_dimensions": self.dimensions,
            },
        )


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.strip().lower()
    if provider == "local":
        return DeterministicLocalEmbeddingProvider()
    if provider == "openai":
        if not settings.openai_api_key:
            raise ProviderConfigurationError(
                "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai."
            )
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_embedding_model,
            dimensions=settings.openai_embedding_dimensions,
        )
    raise ProviderConfigurationError(
        f"Unsupported embedding provider: {settings.embedding_provider}"
    )
