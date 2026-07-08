from pathlib import Path

from fastapi import FastAPI

from trampomemo.answers.routes import create_answer_router
from trampomemo.config import Settings
from trampomemo.database import create_session_factory
from trampomemo.evidence.routes import create_evidence_router
from trampomemo.sources.routes import create_source_router
from trampomemo.sources.source_storage import LocalSourceStorage


def create_app(session_factory=None, source_storage_path: Path | None = None) -> FastAPI:
    settings = Settings()
    app = FastAPI(title="TrampoMemo")
    app.state.session_factory = session_factory or create_session_factory()
    app.state.source_storage = LocalSourceStorage(
        source_storage_path or settings.source_storage_path
    )
    app.include_router(create_source_router())
    app.include_router(create_evidence_router())
    app.include_router(create_answer_router())
    return app


app = create_app()
