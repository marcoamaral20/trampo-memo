from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceRequest(BaseModel):
    question: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class EvidenceResponse(BaseModel):
    id: str
    question: str
    source_id: str
    source_content_id: str
    chunk_id: str
    memory_id: str
    excerpt: str
    rank: int
    relevance_score: float
    trace_metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
