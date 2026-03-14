from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class IngestionCreateRequest(BaseModel):
    entity_type: str = Field(pattern="^(problem|note)$")
    file_id: UUID | None = None
    text_content: str | None = None
    subject: str = Field(default="general", max_length=64)
    source_type: str = Field(default="upload", max_length=32)
    content_category: str = Field(
        default="problem", pattern="^(problem|note|document)$"
    )
    auto_parse: bool = True

    @model_validator(mode="after")
    def validate_input_source(self) -> "IngestionCreateRequest":
        if self.file_id is None and not self.text_content:
            raise ValueError("file_id and text_content cannot both be empty")
        return self


class IngestionCreateData(BaseModel):
    entity_type: str
    entity_id: UUID
    parse_job_id: UUID
    parse_status: str
    content_category: str
