from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol


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
