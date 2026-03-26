import hashlib
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.core.config import get_settings
from app.core.constants import UploadStatus
from app.core.exceptions import ForbiddenException, NotFoundException
from app.db.session import get_db
from app.models.file import FileRecord
from app.schemas.common import ApiResponse
from app.schemas.file import (
    ConfirmUploadData,
    ConfirmUploadRequest,
    LocalUploadData,
    UploadPolicyData,
    UploadPolicyRequest,
)


router = APIRouter(tags=["files"])

ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _sanitize_filename(filename: str) -> str:
    sanitized = filename.strip().replace("\\", "-").replace("/", "-")
    sanitized = re.sub(r"\s+", "-", sanitized)
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "-", sanitized)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-.")
    return sanitized or "upload.bin"


def _build_local_object_key(
    user_id: uuid.UUID, content_category: str, filename: str
) -> str:
    now = datetime.now(UTC)
    safe_filename = _sanitize_filename(filename)
    return "/".join(
        [
            str(user_id),
            content_category,
            f"{now.year:04d}",
            f"{now.month:02d}",
            f"{uuid.uuid4()}-{safe_filename}",
        ]
    )


def _build_file_url(object_key: str) -> str:
    settings = get_settings()
    normalized_key = object_key.lstrip("/")
    return f"{settings.normalized_uploads_url_base}/{normalized_key}"


def _resolve_storage_path(object_key: str) -> Path:
    settings = get_settings()
    normalized_key = object_key.lstrip("/")
    return settings.resolved_uploads_root_dir / Path(normalized_key)


@router.post("/files/upload-policy")
def create_upload_policy(
    payload: UploadPolicyRequest,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[UploadPolicyData]:
    settings = get_settings()
    user_id = uuid.UUID(str(token_payload["sub"]))
    if payload.mime_type not in ALLOWED_MIME_TYPES:
        raise ForbiddenException("unsupported file type")

    object_key = _build_local_object_key(
        user_id=user_id,
        content_category=payload.content_type,
        filename=payload.filename,
    )

    file_record = FileRecord(
        user_id=user_id,
        object_key=object_key,
        storage_provider=settings.storage_provider,
        bucket_name="local",
        file_url=None,
        original_filename=payload.filename,
        mime_type=payload.mime_type,
        file_kind=payload.file_kind,
        content_category=payload.content_type,
        size_bytes=None,
        sha256=None,
        source_type="upload",
        upload_status=UploadStatus.PENDING.value,
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    return ApiResponse(
        data=UploadPolicyData(
            file_id=file_record.id,
            object_key=file_record.object_key,
            upload_url=_build_file_url(file_record.object_key),
            upload_token="local-upload-token",
            max_size_bytes=10 * 1024 * 1024,
            accepted_as=f"{payload.file_kind}:{payload.content_type}",
        )
    )


@router.post("/files/confirm")
def confirm_upload(
    payload: ConfirmUploadRequest,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[ConfirmUploadData]:
    settings = get_settings()
    user_id = uuid.UUID(str(token_payload["sub"]))
    file_record = db.get(FileRecord, payload.file_id)
    if file_record is None:
        raise NotFoundException("file record not found")
    if file_record.user_id != user_id:
        raise ForbiddenException("cannot confirm this file")

    file_record.object_key = payload.object_key.lstrip("/")
    file_record.storage_provider = settings.storage_provider
    file_record.bucket_name = "local"
    file_record.size_bytes = payload.size_bytes
    file_record.mime_type = payload.mime_type
    file_record.sha256 = payload.sha256
    file_record.file_url = _build_file_url(file_record.object_key)
    file_record.upload_status = UploadStatus.CONFIRMED.value
    db.commit()

    return ApiResponse(
        data=ConfirmUploadData(
            file_id=file_record.id,
            file_url=file_record.file_url,
            upload_status=file_record.upload_status,
            file_kind=file_record.file_kind,
            content_category=file_record.content_category,
        )
    )


@router.post("/files/upload-local")
async def upload_local_file(
    file_id: uuid.UUID = Form(...),
    object_key: str = Form(...),
    upload_file: UploadFile = File(...),
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[LocalUploadData]:
    user_id = uuid.UUID(str(token_payload["sub"]))
    file_record = db.get(FileRecord, file_id)
    if file_record is None:
        raise NotFoundException("file record not found")
    if file_record.user_id != user_id:
        raise ForbiddenException("cannot upload this file")
    if file_record.object_key != object_key.lstrip("/"):
        raise ForbiddenException("object_key mismatch")

    target_path = _resolve_storage_path(file_record.object_key)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    payload = await upload_file.read()
    target_path.write_bytes(payload)

    file_record.size_bytes = len(payload)
    file_record.sha256 = hashlib.sha256(payload).hexdigest()
    db.commit()

    return ApiResponse(
        data=LocalUploadData(
            file_id=file_record.id,
            object_key=file_record.object_key,
            bytes_written=len(payload),
        )
    )
