import pytest

from trampomemo.answers.llm_provider import (
    DeterministicLocalLLMProvider,
    OpenAILLMProvider,
    create_llm_provider,
)
from trampomemo.core.config import Settings
from trampomemo.core.provider_errors import ProviderConfigurationError


def test_creates_local_llm_provider_by_default() -> None:
    provider = create_llm_provider(Settings())

    assert isinstance(provider, DeterministicLocalLLMProvider)


def test_creates_openai_llm_provider_from_settings() -> None:
    provider = create_llm_provider(
        Settings(
            llm_provider="openai",
            openai_api_key="sk-test",
        )
    )

    assert isinstance(provider, OpenAILLMProvider)
    assert provider.provider == "openai"
    assert provider.model == "gpt-5.4-mini"


def test_refuses_openai_llm_provider_without_api_key() -> None:
    with pytest.raises(ProviderConfigurationError, match="OPENAI_API_KEY"):
        create_llm_provider(Settings(llm_provider="openai"))


def test_refuses_unknown_llm_provider() -> None:
    with pytest.raises(ProviderConfigurationError, match="Unsupported LLM provider"):
        create_llm_provider(Settings(llm_provider="unknown"))


def test_openai_llm_provider_returns_generated_text(monkeypatch) -> None:
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
            "id": "resp_123",
            "status": "completed",
            "output_text": "Three companies required AWS Lambda.",
            "usage": {"output_tokens": 8},
        }

    monkeypatch.setattr("trampomemo.answers.llm_provider.post_openai_json", fake_post_openai_json)
    provider = OpenAILLMProvider(
        api_key="sk-test",
        base_url="https://api.openai.com/v1",
        model="gpt-5.4-mini",
        max_output_tokens=800,
    )

    result = provider.generate(system_prompt="Use evidence.", user_prompt="Evidence: AWS Lambda")

    assert captured_payload["url"] == "https://api.openai.com/v1/responses"
    assert captured_payload["payload"]["model"] == "gpt-5.4-mini"
    assert captured_payload["payload"]["input"][0]["role"] == "system"
    assert captured_payload["payload"]["input"][1]["role"] == "user"
    assert result.text == "Three companies required AWS Lambda."
    assert result.provider == "openai"
    assert result.metadata["response_id"] == "resp_123"
