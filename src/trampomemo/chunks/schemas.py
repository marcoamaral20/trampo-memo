from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChunkResponse(BaseModel):
    id: str
    source_id: str
    source_content_id: str
    sequence: int
    text: str
    start_char: int
    end_char: int
    character_count: int
    heading_path: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
