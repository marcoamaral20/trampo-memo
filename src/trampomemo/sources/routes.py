from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from trampomemo.core.database import session_dependency
from trampomemo.sources.models import SourceType
from trampomemo.sources.schemas import SourceResponse
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

    return router
