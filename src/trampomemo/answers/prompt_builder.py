from dataclasses import dataclass

from trampomemo.evidence.models import Evidence

SYSTEM_PROMPT = (
    "You answer job search questions using only the supplied Evidence. "
    "If the Evidence is empty, say that there is not enough evidence."
)


@dataclass(frozen=True)
class Prompt:
    system_prompt: str
    user_prompt: str
    metadata: dict


class PromptBuilder:
    def build(self, *, question: str, evidence: list[Evidence]) -> Prompt:
        evidence_lines = [
            f"[{index}] {item.excerpt}" for index, item in enumerate(evidence, start=1)
        ]
        evidence_text = "\n".join(evidence_lines) if evidence_lines else "None."
        user_prompt = "\n\n".join(
            [
                f"Question:\n{question}",
                f"Evidence:\n{evidence_text}",
                "Instructions:\nAnswer using only the Evidence above.",
            ]
        )
        return Prompt(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            metadata={
                "evidence_count": len(evidence),
                "prompt_builder": "trampomemo_prompt_builder_v1",
            },
        )
