from pathlib import Path

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from trampomemo.answers.routes import create_answer_router
from trampomemo.chunks.routes import create_chunk_router
from trampomemo.core.config import Settings
from trampomemo.core.database import create_session_factory
from trampomemo.core.provider_errors import ProviderConfigurationError, ProviderError
from trampomemo.evidence.routes import create_evidence_router
from trampomemo.memory.routes import create_memory_router
from trampomemo.source_content.routes import create_source_content_router
from trampomemo.sources.routes import create_source_router
from trampomemo.sources.source_storage import LocalSourceStorage


def create_app(session_factory=None, source_storage_path: Path | None = None) -> FastAPI:
    settings = Settings()
    app = FastAPI(title="TrampoMemo")
    app.state.settings = settings
    app.state.session_factory = session_factory or create_session_factory()
    app.state.source_storage = LocalSourceStorage(
        source_storage_path or settings.source_storage_path
    )
    app.include_router(create_source_router())
    app.include_router(create_source_content_router())
    app.include_router(create_chunk_router())
    app.include_router(create_memory_router())
    app.include_router(create_evidence_router())
    app.include_router(create_answer_router())

    @app.exception_handler(ProviderConfigurationError)
    def provider_configuration_error_handler(_, exc: ProviderConfigurationError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ProviderError)
    def provider_error_handler(_, exc: ProviderError):
        status_code = (
            exc.status_code if exc.status_code == 429 else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
        )

    return app


app = create_app()
