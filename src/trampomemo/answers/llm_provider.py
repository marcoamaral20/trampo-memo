import re
from dataclasses import dataclass
from typing import Protocol


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
