from sqlalchemy import select
from sqlalchemy.orm import Session

from trampomemo.sources.models import Source


class SourceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, source: Source) -> Source:
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def list(self) -> list[Source]:
        result = self.session.execute(select(Source).order_by(Source.created_at.asc()))
        return list(result.scalars())

    def get(self, source_id: str) -> Source | None:
        return self.session.get(Source, source_id)

    def save(self, source: Source) -> Source:
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source
