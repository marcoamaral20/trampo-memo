from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceResponse(BaseModel):
    id: str
    source_type: str
    source_origin: str
    title: str
    origin: str | None
    original_filename: str | None
    content_type: str | None
    storage_uri: str | None
    status: str
    content_status: str
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


class MemoryResponse(BaseModel):
    id: str
    source_id: str
    chunk_id: str
    model: str
    dimensions: int
    provider: str
    fingerprint: str
    provider_metadata: dict
    vector_preview: list[float]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
