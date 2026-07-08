from sqlalchemy import select
from sqlalchemy.orm import Session

from trampomemo.answers.models import Answer


class AnswerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_for_generation(
        self,
        *,
        question_fingerprint: str,
        evidence_fingerprint: str,
        model: str,
    ) -> Answer | None:
        result = self.session.execute(
            select(Answer).where(
                Answer.question_fingerprint == question_fingerprint,
                Answer.evidence_fingerprint == evidence_fingerprint,
                Answer.model == model,
            )
        )
        return result.scalar_one_or_none()

    def list_all(self) -> list[Answer]:
        result = self.session.execute(select(Answer).order_by(Answer.created_at.asc()))
        return list(result.scalars())

    def save(self, answer: Answer) -> Answer:
        self.session.add(answer)
        self.session.commit()
        self.session.refresh(answer)
        return answer
