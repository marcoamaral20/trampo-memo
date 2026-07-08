from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from trampomemo.chunks.repository import ChunkRepository
from trampomemo.core.database import session_dependency
from trampomemo.memory.embedding_provider import create_embedding_provider
from trampomemo.memory.repository import MemoryRepository
from trampomemo.memory.schemas import MemoryResponse
from trampomemo.memory.service import ChunksRequiredForMemoryError, MemoryService
from trampomemo.source_content.service import SourceNotFoundError
from trampomemo.sources.source_repository import SourceRepository


def create_memory_router() -> APIRouter:
    router = APIRouter(prefix="/sources", tags=["Memory"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_memory_service(
        request: Request,
        session: Annotated[Session, Depends(get_session)],
    ) -> MemoryService:
        return MemoryService(
            source_repository=SourceRepository(session),
            chunk_repository=ChunkRepository(session),
            memory_repository=MemoryRepository(session),
            provider=create_embedding_provider(request.app.state.settings),
        )

    @router.post(
        "/{source_id}/content/chunks/memory",
        response_model=list[MemoryResponse],
        status_code=status.HTTP_201_CREATED,
    )
    def build_memory(
        source_id: str,
        service: Annotated[MemoryService, Depends(get_memory_service)],
    ):
        try:
            return service.build_memory(source_id=source_id)
        except SourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found.",
            ) from exc
        except ChunksRequiredForMemoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chunks must exist before Memory can be built.",
            ) from exc

    @router.get("/{source_id}/content/chunks/memory", response_model=list[MemoryResponse])
    def list_memory(
        source_id: str,
        service: Annotated[MemoryService, Depends(get_memory_service)],
    ):
        try:
            return service.list_memory(source_id=source_id)
        except SourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found.",
            ) from exc

    return router
