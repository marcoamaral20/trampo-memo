from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from trampomemo.core.database import session_dependency
from trampomemo.source_content.repository import SourceContentRepository
from trampomemo.source_content.schemas import SourceContentResponse
from trampomemo.source_content.service import (
    SourceCannotProduceContentError,
    SourceContentNotFoundError,
    SourceContentService,
    SourceNotFoundError,
)
from trampomemo.sources.source_repository import SourceRepository


def create_source_content_router() -> APIRouter:
    router = APIRouter(prefix="/sources", tags=["SourceContent"])

    def get_session(request: Request):
        yield from session_dependency(request.app.state.session_factory)

    def get_source_content_service(
        request: Request,
        session: Annotated[Session, Depends(get_session)],
    ) -> SourceContentService:
        return SourceContentService(
            source_repository=SourceRepository(session),
            content_repository=SourceContentRepository(session),
            storage=request.app.state.source_storage,
        )

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

    return router
