from sqlalchemy import select
from sqlalchemy.orm import Session

from trampomemo.source_content.models import SourceContent


class SourceContentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_source_id(self, source_id: str) -> SourceContent | None:
        result = self.session.execute(
            select(SourceContent).where(SourceContent.source_id == source_id)
        )
        return result.scalar_one_or_none()

    def save(self, source_content: SourceContent) -> SourceContent:
        self.session.add(source_content)
        self.session.commit()
        self.session.refresh(source_content)
        return source_content
