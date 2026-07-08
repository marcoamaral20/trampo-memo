from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from trampomemo.answers.answer_repository import AnswerRepository
from trampomemo.answers.answer_service import AnswerService
from trampomemo.answers.schemas import AnswerRequest, AnswerResponse
from trampomemo.database import session_dependency
from trampomemo.evidence.evidence_repository import EvidenceRepository
from trampomemo.evidence.evidence_service import EvidenceService
from trampomemo.sources.chunk_repository import ChunkRepository
from trampomemo.sources.memory_repository import MemoryRepository


def create_answer_router() -> APIRouter:
    router = APIRouter(prefix="/answers", tags=["Answers"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_answer_service(
        session: Annotated[Session, Depends(get_session)],
    ) -> AnswerService:
        evidence_service = EvidenceService(
            memory_repository=MemoryRepository(session),
            chunk_repository=ChunkRepository(session),
            evidence_repository=EvidenceRepository(session),
        )
        return AnswerService(
            evidence_service=evidence_service,
            answer_repository=AnswerRepository(session),
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
