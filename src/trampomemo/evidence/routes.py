from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from trampomemo.core.database import session_dependency
from trampomemo.evidence.repository import EvidenceRepository
from trampomemo.evidence.schemas import EvidenceRequest, EvidenceResponse
from trampomemo.evidence.service import EvidenceService
from trampomemo.memory.embedding_provider import create_embedding_provider
from trampomemo.memory.repository import MemoryRepository


def create_evidence_router() -> APIRouter:
    router = APIRouter(prefix="/evidence", tags=["Evidence"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_evidence_service(
        request: Request,
        session: Annotated[Session, Depends(get_session)],
    ) -> EvidenceService:
        return EvidenceService(
            memory_repository=MemoryRepository(session),
            evidence_repository=EvidenceRepository(session),
            provider=create_embedding_provider(request.app.state.settings),
        )

    @router.post("", response_model=list[EvidenceResponse], status_code=status.HTTP_201_CREATED)
    def construct_evidence(
        request: EvidenceRequest,
        service: Annotated[EvidenceService, Depends(get_evidence_service)],
    ):
        return service.construct_evidence(question=request.question, limit=request.limit)

    @router.get("", response_model=list[EvidenceResponse])
    def list_evidence(
        service: Annotated[EvidenceService, Depends(get_evidence_service)],
    ):
        return service.list_evidence()

    return router
