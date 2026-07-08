from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceContentResponse(BaseModel):
    id: str
    source_id: str
    text: str
    status: str
    failure_reason: str | None
    character_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
