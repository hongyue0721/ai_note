from uuid import UUID

from pydantic import BaseModel, Field


class UploadPolicyRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=128)
    content_type: str = Field(min_length=1, max_length=32)
    file_kind: str = Field(pattern="^(image|document)$")


class UploadPolicyData(BaseModel):
    file_id: UUID
    object_key: str
    upload_url: str
    upload_token: str
    max_size_bytes: int
    accepted_as: str


class ConfirmUploadRequest(BaseModel):
    file_id: UUID
    object_key: str
    size_bytes: int
    mime_type: str
    sha256: str


class ConfirmUploadData(BaseModel):
    file_id: UUID
    file_url: str | None
    upload_status: str
    file_kind: str
    content_category: str


class LocalUploadData(BaseModel):
    file_id: UUID
    object_key: str
    bytes_written: int
