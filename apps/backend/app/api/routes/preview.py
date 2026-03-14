import uuid
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.db.session import get_db
from app.models.file import FileRecord
from app.schemas.common import ApiResponse
from app.schemas.preview import UploadPreviewData, UploadPreviewRequest
from app.services.classifier import classify_content
from app.services.llm_client import OpenAIClient


router = APIRouter(tags=["preview"])


def _resolve_storage_path(object_key: str) -> Path:
    settings = get_settings()
    normalized_key = object_key.lstrip("/")
    return settings.resolved_uploads_root_dir / Path(normalized_key)


@router.post("/preview/upload-tags")
def preview_upload_tags(
    payload: UploadPreviewRequest,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[UploadPreviewData]:
    user_id = uuid.UUID(str(token_payload["sub"]))
    text_content = (payload.text_content or "").strip()

    image_bytes: bytes | None = None
    if payload.file_id is not None:
        file_record = db.get(FileRecord, payload.file_id)
        if file_record is None:
            raise NotFoundException("file record not found")
        if file_record.user_id != user_id:
            raise ForbiddenException("cannot preview this file")

        if payload.file_kind == "image":
            file_path = _resolve_storage_path(file_record.object_key)
            if not file_path.exists():
                raise NotFoundException("uploaded file not found")
            image_bytes = file_path.read_bytes()

    if (
        payload.file_kind == "image"
        and image_bytes is not None
        and get_settings().openai_api_key
    ):
        client = OpenAIClient()
        classification, model_name = classify_content(
            text_content=text_content or "请结合图片内容提取标签与分类。",
            file_kind=payload.file_kind,
            content_category=payload.content_type,
            image_bytes=image_bytes,
            image_mime_type=payload.mime_type,
            llm_client=client,
        )
    else:
        classification, model_name = classify_content(
            text_content=text_content or "未提供正文内容",
            file_kind=payload.file_kind,
            content_category=payload.content_type,
        )

    result = classification.model_dump(mode="json")
    result["subject"] = payload.subject or result["subject"]
    result["model"] = model_name
    return ApiResponse(data=UploadPreviewData.model_validate(result))
