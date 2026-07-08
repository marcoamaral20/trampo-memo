from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from trampomemo.database import session_dependency
from trampomemo.sources.chunk_repository import ChunkRepository
from trampomemo.sources.chunk_service import ChunkService, SourceContentCannotProduceChunksError
from trampomemo.sources.memory_builder import ChunksRequiredForMemoryError, MemoryBuilder
from trampomemo.sources.memory_repository import MemoryRepository
from trampomemo.sources.models import SourceType
from trampomemo.sources.schemas import (
    ChunkResponse,
    MemoryResponse,
    SourceContentResponse,
    SourceResponse,
)
from trampomemo.sources.source_content_repository import SourceContentRepository
from trampomemo.sources.source_content_service import (
    SourceCannotProduceContentError,
    SourceContentNotFoundError,
    SourceContentService,
    SourceNotFoundError,
)
from trampomemo.sources.source_repository import SourceRepository
from trampomemo.sources.source_service import FileInput, SourceService


def create_source_router() -> APIRouter:
    router = APIRouter(prefix="/sources", tags=["Sources"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_source_service(
        request: Request,
        session: Annotated[Session, Depends(get_session)],
    ) -> SourceService:
        return SourceService(
            repository=SourceRepository(session),
            storage=request.app.state.source_storage,
        )

    def get_source_content_service(
        request: Request,
        session: Annotated[Session, Depends(get_session)],
    ) -> SourceContentService:
        return SourceContentService(
            source_repository=SourceRepository(session),
            content_repository=SourceContentRepository(session),
            storage=request.app.state.source_storage,
        )

    def get_chunk_service(
        session: Annotated[Session, Depends(get_session)],
    ) -> ChunkService:
        return ChunkService(
            source_repository=SourceRepository(session),
            content_repository=SourceContentRepository(session),
            chunk_repository=ChunkRepository(session),
        )

    def get_memory_builder(
        session: Annotated[Session, Depends(get_session)],
    ) -> MemoryBuilder:
        return MemoryBuilder(
            source_repository=SourceRepository(session),
            chunk_repository=ChunkRepository(session),
            memory_repository=MemoryRepository(session),
        )

    @router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
    async def create_source(
        service: Annotated[SourceService, Depends(get_source_service)],
        source_type: Annotated[SourceType, Form()],
        title: Annotated[str, Form()],
        origin: Annotated[str | None, Form()] = None,
        text: Annotated[str | None, Form()] = None,
        file: Annotated[UploadFile | None, File()] = None,
    ):
        file_input = None
        if file is not None:
            file_input = FileInput(
                filename=file.filename or "source",
                content_type=file.content_type,
                content=await file.read(),
            )

        try:
            return service.create_source(
                source_type=source_type,
                title=title,
                origin=origin,
                text=text,
                file=file_input,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.get("", response_model=list[SourceResponse])
    def list_sources(service: Annotated[SourceService, Depends(get_source_service)]):
        return service.list_sources()

    @router.post(
        "/{source_id}/content",
        response_model=SourceContentResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_source_content(
        source_id: str,
        service: Annotated[SourceContentService, Depends(get_source_content_service)],
    ):
        try:
            return service.create_source_content(source_id=source_id)
        except SourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found.",
            ) from exc
        except SourceCannotProduceContentError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only imported Sources can produce SourceContent.",
            ) from exc

    @router.get("/{source_id}/content", response_model=SourceContentResponse)
    def get_source_content(
        source_id: str,
        service: Annotated[SourceContentService, Depends(get_source_content_service)],
    ):
        try:
            return service.get_source_content(source_id=source_id)
        except SourceContentNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SourceContent not found.",
            ) from exc

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

    @router.post(
        "/{source_id}/content/chunks/memory",
        response_model=list[MemoryResponse],
        status_code=status.HTTP_201_CREATED,
    )
    def build_memory(
        source_id: str,
        service: Annotated[MemoryBuilder, Depends(get_memory_builder)],
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
        service: Annotated[MemoryBuilder, Depends(get_memory_builder)],
    ):
        try:
            return service.list_memory(source_id=source_id)
        except SourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found.",
            ) from exc

    return router
