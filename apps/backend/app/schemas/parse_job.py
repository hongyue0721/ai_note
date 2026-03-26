from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ParseJobResultData(BaseModel):
    id: UUID
    status: str
    entity_type: str
    entity_id: UUID
    content_category: str | None = None
    result: dict | None = None
    error_message: str | None = None
    attempt_count: int
    created_at: datetime
    updated_at: datetime


class ParseJobRetryData(BaseModel):
    id: UUID
    status: str
    attempt_count: int


class ParseJobListItem(BaseModel):
    id: UUID
    status: str
    entity_type: str
    entity_id: UUID
    content_category: str | None = None
    attempt_count: int
    error_message: str | None = None
    created_at: datetime
