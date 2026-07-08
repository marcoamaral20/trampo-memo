from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from trampomemo.chunks.repository import ChunkRepository
from trampomemo.chunks.schemas import ChunkResponse
from trampomemo.chunks.service import ChunkService, SourceContentCannotProduceChunksError
from trampomemo.core.database import session_dependency
from trampomemo.source_content.repository import SourceContentRepository
from trampomemo.source_content.service import SourceContentNotFoundError, SourceNotFoundError
from trampomemo.sources.source_repository import SourceRepository


def create_chunk_router() -> APIRouter:
    router = APIRouter(prefix="/sources", tags=["Chunks"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_chunk_service(
        session: Annotated[Session, Depends(get_session)],
    ) -> ChunkService:
        return ChunkService(
            source_repository=SourceRepository(session),
            content_repository=SourceContentRepository(session),
            chunk_repository=ChunkRepository(session),
        )

    @router.post(
        "/{source_id}/content/chunks",
        response_model=list[ChunkResponse],
        status_code=status.HTTP_201_CREATED,
    )
    def create_chunks(
        source_id: str,
        service: Annotated[ChunkService, Depends(get_chunk_service)],
    ):
        try:
            return service.create_chunks(source_id=source_id)
        except SourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found.",
            ) from exc
        except SourceContentNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SourceContent not found.",
            ) from exc
        except SourceContentCannotProduceChunksError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only ready SourceContent can produce Chunks.",
            ) from exc

    @router.get("/{source_id}/content/chunks", response_model=list[ChunkResponse])
    def list_chunks(
        source_id: str,
        service: Annotated[ChunkService, Depends(get_chunk_service)],
    ):
        try:
            return service.list_chunks(source_id=source_id)
        except SourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found.",
            ) from exc
        except SourceContentNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SourceContent not found.",
            ) from exc

    return router
