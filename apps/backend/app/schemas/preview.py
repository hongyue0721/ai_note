from uuid import UUID

from pydantic import BaseModel, Field


class UploadPreviewRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=128)
    file_kind: str = Field(pattern="^(image|document)$")
    content_type: str = Field(pattern="^(problem|note|document)$")
    subject: str = Field(default="general", max_length=64)
    text_content: str | None = None
    file_id: UUID | None = None


class KnowledgeCandidateData(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)


class UploadPreviewData(BaseModel):
    entity_type: str
    content_category: str
    subject: str
    title: str
    normalized_text: str
    knowledge_candidates: list[KnowledgeCandidateData]
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = False
    review_reason: str | None = None
