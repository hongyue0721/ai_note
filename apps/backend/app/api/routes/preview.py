import uuid
from pathlib import Path

from fastapi import APIRouter, Depends
from pypdf import PdfReader
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


def _read_file_text(file_record: FileRecord) -> str:
    file_path = _resolve_storage_path(file_record.object_key)
    if not file_path.exists():
        return ""

    mime_type = file_record.mime_type or ""
    try:
        if mime_type == "text/plain":
            return file_path.read_text(encoding="utf-8", errors="ignore").strip()
        if mime_type == "application/pdf":
            reader = PdfReader(str(file_path))
            parts: list[str] = []
            for page in reader.pages[:6]:
                parts.append((page.extract_text() or "").strip())
            return "\n".join(part for part in parts if part).strip()
    except Exception:
        return ""

    return ""


def _build_summary(text: str) -> str:
    normalized = " ".join(text.split())
    if not normalized:
        return ""
    return normalized[:120]


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

        extracted_text = _read_file_text(file_record)
        if extracted_text and not text_content:
            text_content = extracted_text

        if payload.file_kind == "image":
            file_path = _resolve_storage_path(file_record.object_key)
            if not file_path.exists():
                raise NotFoundException("uploaded file not found")
            image_bytes = file_path.read_bytes()

    runtime_classify = None
    try:
        from app.services.runtime_config import get_runtime_scope_config

        runtime_classify = get_runtime_scope_config(db, "classify")
    except Exception:
        runtime_classify = None

    if (
        payload.file_kind == "image"
        and image_bytes is not None
        and (
            (runtime_classify and runtime_classify.api_key)
            or get_settings().openai_api_key
        )
    ):
        client = (
            OpenAIClient(runtime_config=runtime_classify)
            if runtime_classify
            else OpenAIClient()
        )
        classification, model_name = classify_content(
            text_content=text_content or "请结合图片内容提取标签与分类。",
            file_kind=payload.file_kind,
            content_category=payload.content_type,
            db=db,
            image_bytes=image_bytes,
            image_mime_type=payload.mime_type,
            llm_client=client,
        )
    else:
        classification, model_name = classify_content(
            text_content=text_content or "未提供正文内容",
            file_kind=payload.file_kind,
            content_category=payload.content_type,
            db=db,
        )

    result = classification.model_dump(mode="json")
    result["subject"] = payload.subject or result["subject"]
    result["summary"] = _build_summary(result.get("normalized_text", text_content))
    result["model"] = model_name
    result["needs_review"] = False
    result["review_reason"] = ""
    return ApiResponse(data=UploadPreviewData.model_validate(result))
