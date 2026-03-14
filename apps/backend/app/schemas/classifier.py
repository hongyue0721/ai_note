from pydantic import BaseModel, Field


class KnowledgeCandidate(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)


class ClassificationResult(BaseModel):
    entity_type: str = Field(pattern="^(problem|note)$")
    content_category: str = Field(pattern="^(problem|note|document)$")
    subject: str
    title: str
    normalized_text: str
    knowledge_candidates: list[KnowledgeCandidate]
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = False
    review_reason: str | None = None
