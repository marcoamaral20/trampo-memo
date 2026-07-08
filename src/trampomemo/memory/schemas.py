from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
