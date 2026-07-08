from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from trampomemo.database import session_dependency
from trampomemo.evidence.evidence_repository import EvidenceRepository
from trampomemo.evidence.evidence_service import EvidenceService
from trampomemo.evidence.schemas import EvidenceRequest, EvidenceResponse
from trampomemo.sources.chunk_repository import ChunkRepository
from trampomemo.sources.memory_repository import MemoryRepository


def create_evidence_router() -> APIRouter:
    router = APIRouter(prefix="/evidence", tags=["Evidence"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_evidence_service(
        session: Annotated[Session, Depends(get_session)],
    ) -> EvidenceService:
        return EvidenceService(
            memory_repository=MemoryRepository(session),
            chunk_repository=ChunkRepository(session),
            evidence_repository=EvidenceRepository(session),
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
