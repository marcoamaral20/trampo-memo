from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


class TestSessionFactory:
    def __init__(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self._sessionmaker = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )

    def __call__(self) -> Generator[Session]:
        with self._sessionmaker() as session:
            yield session


@pytest.fixture
def test_session_factory() -> TestSessionFactory:
    return TestSessionFactory()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
