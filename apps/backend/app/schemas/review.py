from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewTaskItem(BaseModel):
    id: UUID
    task_type: str
    entity_type: str
    entity_id: UUID
    status: str
    payload_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class ReviewDecisionRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject|replace)$")
    edited_tags: list[dict] = Field(default_factory=list)


class ReviewDecisionData(BaseModel):
    id: UUID
    status: str
