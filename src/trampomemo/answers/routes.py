from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from trampomemo.answers.llm_provider import create_llm_provider
from trampomemo.answers.repository import AnswerRepository
from trampomemo.answers.schemas import AnswerRequest, AnswerResponse
from trampomemo.answers.service import AnswerService
from trampomemo.core.database import session_dependency
from trampomemo.evidence.repository import EvidenceRepository
from trampomemo.evidence.service import EvidenceService
from trampomemo.memory.embedding_provider import create_embedding_provider
from trampomemo.memory.repository import MemoryRepository


def create_answer_router() -> APIRouter:
    router = APIRouter(prefix="/answers", tags=["Answers"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_answer_service(
        request: Request,
        session: Annotated[Session, Depends(get_session)],
    ) -> AnswerService:
        evidence_service = EvidenceService(
            memory_repository=MemoryRepository(session),
            evidence_repository=EvidenceRepository(session),
            provider=create_embedding_provider(request.app.state.settings),
        )
        return AnswerService(
            evidence_service=evidence_service,
            answer_repository=AnswerRepository(session),
            provider=create_llm_provider(request.app.state.settings),
        )

    @router.post("", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
    def construct_answer(
        request: AnswerRequest,
        service: Annotated[AnswerService, Depends(get_answer_service)],
    ):
        return service.construct_answer(
            question=request.question,
            evidence_limit=request.evidence_limit,
        )

    @router.get("", response_model=list[AnswerResponse])
    def list_answers(
        service: Annotated[AnswerService, Depends(get_answer_service)],
    ):
        return service.list_answers()

    return router
