from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1)
    evidence_limit: int = Field(default=5, ge=1, le=20)


class AnswerResponse(BaseModel):
    id: str
    question: str
    text: str
    evidence_ids: list[str]
    provider: str
    model: str
    provider_metadata: dict
    generation_metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
