import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.core.config import get_settings
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.file import FileRecord
from app.models.note import Note
from app.models.parse_job import ParseJob
from app.models.review_task import ReviewTask
from app.schemas.classifier import ClassificationResult
from app.schemas.common import ApiResponse
from app.schemas.content import (
    ContentTagData,
    NoteDetailData,
    NoteListItem,
    NoteUpdateRequest,
)
from app.schemas.preview import UploadPreviewData
from app.core.constants import ParseJobStatus
from app.services.canonical_tags import (
    get_entity_canonical_tags,
    sync_entity_canonical_tags,
)


router = APIRouter(tags=["notes"])


class NoteConfirmRequest(UploadPreviewData):
    file_id: UUID | None = None
    source_type: str = "upload"


def _get_note_tags(db: Session, note_id: UUID) -> list[ContentTagData]:
    return get_entity_canonical_tags(db, entity_type="note", entity_id=note_id)


def _normalized_file_url(file_record: FileRecord | None) -> str | None:
    if file_record is None:
        return None
    current = file_record.file_url or ""
    if current.startswith(get_settings().normalized_uploads_url_base):
        return current
    normalized_key = file_record.object_key.lstrip("/")
    return f"{get_settings().normalized_uploads_url_base}/{normalized_key}"


def _build_note_data(item: Note) -> NoteDetailData:
    raise RuntimeError("_build_note_data requires db session")


def _build_note_data_with_db(db: Session, item: Note) -> NoteDetailData:
    file_record = db.get(FileRecord, item.file_id) if item.file_id else None
    tags = _get_note_tags(db, item.id)

    return NoteDetailData(
        id=item.id,
        title=item.title,
        subject=item.subject,
        category=item.category,
        parse_status=item.parse_status,
        raw_text=item.raw_text,
        cleaned_text=item.cleaned_text,
        file_id=item.file_id,
        file_url=_normalized_file_url(file_record),
        original_filename=file_record.original_filename if file_record else None,
        mime_type=file_record.mime_type if file_record else None,
        file_kind=file_record.file_kind if file_record else None,
        tags=tags,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/notes")
def list_notes(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
    subject: str | None = Query(default=None),
    category: str | None = Query(default=None),
) -> ApiResponse[list[NoteListItem]]:
    user_id = UUID(str(token_payload["sub"]))
    stmt = select(Note).where(Note.user_id == user_id).order_by(Note.created_at.desc())
    if subject:
        stmt = stmt.where(Note.subject == subject)
    if category:
        stmt = stmt.where(Note.category == category)

    items = db.scalars(stmt).all()
    return ApiResponse(
        data=[
            NoteListItem(**_build_note_data_with_db(db, item).model_dump(mode="json"))
            for item in items
        ]
    )


@router.get("/notes/{note_id}")
def get_note(
    note_id: UUID,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[NoteDetailData]:
    item = db.get(Note, note_id)
    if item is None:
        raise NotFoundException("note not found")
    if item.user_id != UUID(str(token_payload["sub"])):
        raise NotFoundException("note not found")

    return ApiResponse(data=_build_note_data_with_db(db, item))


@router.patch("/notes/{note_id}")
def update_note(
    note_id: UUID,
    payload: NoteUpdateRequest,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[NoteDetailData]:
    item = db.get(Note, note_id)
    if item is None:
        raise NotFoundException("note not found")
    if item.user_id != UUID(str(token_payload["sub"])):
        raise NotFoundException("note not found")

    payload_data = payload.model_dump(exclude_none=True)
    next_tags = payload_data.pop("tags", None)
    for field, value in payload_data.items():
        setattr(item, field, value)
    if next_tags is not None:
        sync_entity_canonical_tags(
            db,
            entity_type="note",
            entity_id=item.id,
            tags=next_tags,
        )
    db.commit()
    db.refresh(item)

    return ApiResponse(data=_build_note_data_with_db(db, item))


@router.delete("/notes/{note_id}")
def delete_note(
    note_id: UUID,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, str]]:
    item = db.get(Note, note_id)
    if item is None:
        raise NotFoundException("note not found")
    if item.user_id != UUID(str(token_payload["sub"])):
        raise NotFoundException("note not found")

    parse_jobs = db.scalars(
        select(ParseJob).where(
            ParseJob.entity_type == "note", ParseJob.entity_id == note_id
        )
    ).all()
    for job in parse_jobs:
        db.delete(job)

    review_tasks = db.scalars(
        select(ReviewTask).where(
            ReviewTask.entity_type == "note", ReviewTask.entity_id == note_id
        )
    ).all()
    for task in review_tasks:
        db.delete(task)

    db.delete(item)
    db.commit()
    return ApiResponse(data={"id": str(note_id), "status": "deleted"})


@router.post("/notes/confirm")
def confirm_note_from_preview(
    payload: NoteConfirmRequest,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[NoteDetailData]:
    user_id = uuid.UUID(str(token_payload["sub"]))

    item = Note(
        user_id=user_id,
        file_id=payload.file_id,
        title=payload.title,
        category=payload.content_category,
        subject=payload.subject,
        raw_text=payload.normalized_text,
        cleaned_text=payload.normalized_text,
        parse_status=ParseJobStatus.SUCCESS.value,
        source_type=payload.source_type,
    )
    db.add(item)
    db.flush()

    parse_job = ParseJob(
        user_id=user_id,
        entity_type="note",
        entity_id=item.id,
        file_id=payload.file_id,
        status=ParseJobStatus.SUCCESS.value,
        attempt_count=1,
        llm_model=None,
        request_payload_json={
            "content_category": payload.content_category,
            "subject": payload.subject,
            "source_type": payload.source_type,
        },
        result_json=ClassificationResult(
            entity_type="note",
            content_category=payload.content_category,
            subject=payload.subject,
            title=payload.title,
            normalized_text=payload.normalized_text,
            knowledge_candidates=[
                item.model_dump(mode="json") for item in payload.knowledge_candidates
            ],
            confidence=payload.confidence,
            needs_review=payload.needs_review,
            review_reason=payload.review_reason,
        ).model_dump(mode="json"),
        error_message=None,
        started_at=item.created_at,
        finished_at=item.created_at,
    )
    db.add(parse_job)
    sync_entity_canonical_tags(
        db,
        entity_type="note",
        entity_id=item.id,
        tags=payload.knowledge_candidates,
    )
    db.commit()
    db.refresh(item)

    return ApiResponse(data=_build_note_data_with_db(db, item))
