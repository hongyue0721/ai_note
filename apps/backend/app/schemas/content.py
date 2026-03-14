from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ContentTagData(BaseModel):
    name: str
    confidence: float


class ProblemListItem(BaseModel):
    id: UUID
    title: str | None
    subject: str
    category: str
    parse_status: str
    stem_text: str | None
    created_at: datetime


class ProblemDetailData(BaseModel):
    id: UUID
    title: str | None
    subject: str
    category: str
    parse_status: str
    stem_text: str | None
    normalized_stem: str | None
    answer_text: str | None
    explanation_text: str | None
    created_at: datetime
    updated_at: datetime


class NoteListItem(BaseModel):
    id: UUID
    title: str | None
    subject: str
    category: str
    parse_status: str
    raw_text: str | None
    file_id: UUID | None = None
    file_url: str | None = None
    original_filename: str | None = None
    mime_type: str | None = None
    file_kind: str | None = None
    tags: list[ContentTagData] = []
    created_at: datetime


class NoteDetailData(BaseModel):
    id: UUID
    title: str | None
    subject: str
    category: str
    parse_status: str
    raw_text: str | None
    cleaned_text: str | None
    file_id: UUID | None = None
    file_url: str | None = None
    original_filename: str | None = None
    mime_type: str | None = None
    file_kind: str | None = None
    tags: list[ContentTagData] = []
    created_at: datetime
    updated_at: datetime


class ProblemUpdateRequest(BaseModel):
    title: str | None = None
    subject: str | None = None
    category: str | None = None
    stem_text: str | None = None
    answer_text: str | None = None
    explanation_text: str | None = None


class NoteUpdateRequest(BaseModel):
    title: str | None = None
    subject: str | None = None
    category: str | None = None
    raw_text: str | None = None
    cleaned_text: str | None = None
