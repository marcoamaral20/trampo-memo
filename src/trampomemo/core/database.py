from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from trampomemo.core.config import Settings


def create_session_factory(database_url: str | None = None):
    settings = Settings()
    engine = create_engine(database_url or settings.database_url)
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def session_dependency(session_factory) -> Generator[Session]:
    session_or_generator = session_factory()
    if hasattr(session_or_generator, "__enter__"):
        with session_or_generator as session:
            yield session
        return

    yield from session_or_generator
