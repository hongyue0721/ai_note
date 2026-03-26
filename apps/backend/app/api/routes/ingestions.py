import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.core.constants import ParseJobStatus
from app.db.session import get_db
from app.models.note import Note
from app.models.parse_job import ParseJob
from app.models.problem import Problem
from app.schemas.common import ApiResponse
from app.schemas.ingestion import IngestionCreateData, IngestionCreateRequest


router = APIRouter(tags=["ingestions"])


@router.post("/ingestions")
def create_ingestion(
    payload: IngestionCreateRequest,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[IngestionCreateData]:
    user_id = uuid.UUID(str(token_payload["sub"]))

    if payload.entity_type == "note":
        entity = Note(
            user_id=user_id,
            file_id=payload.file_id,
            title=None,
            category=payload.content_category,
            subject=payload.subject,
            raw_text=payload.text_content,
            cleaned_text=None,
            parse_status=ParseJobStatus.PENDING.value,
            source_type=payload.source_type,
        )
    else:
        entity = Problem(
            user_id=user_id,
            file_id=payload.file_id,
            title=None,
            category=payload.content_category,
            subject=payload.subject,
            stem_text=payload.text_content,
            normalized_stem=None,
            answer_text=None,
            explanation_text=None,
            difficulty=None,
            question_type=None,
            parse_status=ParseJobStatus.PENDING.value,
            source_type=payload.source_type,
        )

    db.add(entity)
    db.flush()

    parse_job = None
    if payload.auto_parse:
        parse_job = ParseJob(
            user_id=user_id,
            entity_type=payload.entity_type,
            entity_id=entity.id,
            file_id=payload.file_id,
            status=ParseJobStatus.PENDING.value,
            attempt_count=0,
            llm_model=None,
            request_payload_json=payload.model_dump(mode="json"),
            result_json=None,
            error_message=None,
            started_at=None,
            finished_at=None,
        )
        db.add(parse_job)
    else:
        entity.parse_status = "skipped"
    db.commit()

    if parse_job is not None:
        db.refresh(parse_job)

    return ApiResponse(
        data=IngestionCreateData(
            entity_type=payload.entity_type,
            entity_id=entity.id,
            parse_job_id=parse_job.id if parse_job is not None else None,
            parse_status=parse_job.status
            if parse_job is not None
            else entity.parse_status,
            content_category=payload.content_category,
        )
    )
