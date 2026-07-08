import re
from dataclasses import dataclass
from typing import Protocol

from trampomemo.core.config import Settings
from trampomemo.core.openai_http import post_openai_json
from trampomemo.core.provider_errors import ProviderConfigurationError


@dataclass(frozen=True)
class LLMProviderResult:
    text: str
    model: str
    provider: str
    metadata: dict


class LLMProvider(Protocol):
    def generate(self, *, system_prompt: str, user_prompt: str) -> LLMProviderResult:
        raise NotImplementedError


class DeterministicLocalLLMProvider:
    provider = "trampomemo-local"
    model = "trampomemo-local-answer-deterministic-v1"

    def generate(self, *, system_prompt: str, user_prompt: str) -> LLMProviderResult:
        evidence = _extract_evidence(user_prompt)
        if not evidence:
            text = "I do not have enough evidence to answer this question."
        else:
            text = "Based on the available evidence: " + " ".join(evidence)

        return LLMProviderResult(
            text=text,
            model=self.model,
            provider=self.provider,
            metadata={
                "purpose": "development_and_test",
                "semantic_model": False,
            },
        )


class OpenAILLMProvider:
    provider = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        max_output_tokens: int,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_output_tokens = max_output_tokens

    def generate(self, *, system_prompt: str, user_prompt: str) -> LLMProviderResult:
        response = post_openai_json(
            url=f"{self.base_url}/responses",
            api_key=self.api_key,
            payload={
                "model": self.model,
                "max_output_tokens": self.max_output_tokens,
                "input": [
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": system_prompt}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": user_prompt}],
                    },
                ],
            },
            provider=self.provider,
        )
        return LLMProviderResult(
            text=_extract_response_text(response),
            model=self.model,
            provider=self.provider,
            metadata={
                "response_id": response.get("id"),
                "status": response.get("status"),
                "usage": response.get("usage", {}),
            },
        )


def create_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.strip().lower()
    if provider == "local":
        return DeterministicLocalLLMProvider()
    if provider == "openai":
        if not settings.openai_api_key:
            raise ProviderConfigurationError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        return OpenAILLMProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_llm_model,
            max_output_tokens=settings.openai_llm_max_output_tokens,
        )
    raise ProviderConfigurationError(f"Unsupported LLM provider: {settings.llm_provider}")


def _extract_evidence(user_prompt: str) -> list[str]:
    evidence_section = user_prompt.split("Evidence:\n", maxsplit=1)[-1]
    evidence_section = evidence_section.split("\n\nInstructions:", maxsplit=1)[0]
    if evidence_section.strip() == "None.":
        return []

    evidence_lines: list[str] = []
    for line in evidence_section.splitlines():
        match = re.match(r"^\[\d+\]\s+(?P<excerpt>.+)$", line)
        if match is not None:
            evidence_lines.append(match.group("excerpt"))
    return evidence_lines


def _extract_response_text(response: dict) -> str:
    output_text = response.get("output_text")
    if isinstance(output_text, str):
        return output_text

    text_parts: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                text_parts.append(text)
    return "\n".join(text_parts).strip()
