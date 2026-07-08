from hashlib import sha256
from uuid import NAMESPACE_URL, uuid5

from trampomemo.answers.answer_repository import AnswerRepository
from trampomemo.answers.llm_provider import DeterministicLocalLLMProvider, LLMProvider
from trampomemo.answers.prompt_builder import PromptBuilder
from trampomemo.evidence.evidence_service import EvidenceService
from trampomemo.sources.models import Answer


class AnswerService:
    def __init__(
        self,
        *,
        evidence_service: EvidenceService,
        answer_repository: AnswerRepository,
        prompt_builder: PromptBuilder | None = None,
        provider: LLMProvider | None = None,
    ) -> None:
        self.evidence_service = evidence_service
        self.answer_repository = answer_repository
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.provider = provider or DeterministicLocalLLMProvider()

    def construct_answer(self, *, question: str, evidence_limit: int) -> Answer:
        normalized_question = question.strip()
        evidence = self.evidence_service.construct_evidence(
            question=normalized_question,
            limit=evidence_limit,
        )
        prompt = self.prompt_builder.build(question=normalized_question, evidence=evidence)
        provider_result = self.provider.generate(
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
        )

        evidence_ids = [item.id for item in evidence]
        question_fingerprint = _fingerprint(normalized_question)
        evidence_fingerprint = _fingerprint("|".join(evidence_ids))
        existing = self.answer_repository.get_for_generation(
            question_fingerprint=question_fingerprint,
            evidence_fingerprint=evidence_fingerprint,
            model=provider_result.model,
        )
        if existing is not None:
            return existing

        answer = Answer(
            id=_stable_answer_id(
                question_fingerprint=question_fingerprint,
                evidence_fingerprint=evidence_fingerprint,
                model=provider_result.model,
            ),
            question=normalized_question,
            question_fingerprint=question_fingerprint,
            text=provider_result.text,
            evidence_ids=evidence_ids,
            evidence_fingerprint=evidence_fingerprint,
            provider=provider_result.provider,
            model=provider_result.model,
            provider_metadata=provider_result.metadata,
            generation_metadata={
                **prompt.metadata,
                "evidence_ids": evidence_ids,
            },
        )
        return self.answer_repository.save(answer)

    def list_answers(self) -> list[Answer]:
        return self.answer_repository.list_all()


def _fingerprint(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _stable_answer_id(*, question_fingerprint: str, evidence_fingerprint: str, model: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{question_fingerprint}:{evidence_fingerprint}:{model}"))
