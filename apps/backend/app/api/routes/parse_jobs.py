from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin_token, require_user_token
from app.core.constants import ParseJobStatus
from app.core.exceptions import ConflictException, NotFoundException
from app.db.session import get_db
from app.models.parse_job import ParseJob
from app.schemas.common import ApiResponse
from app.schemas.parse_job import (
    ParseJobListItem,
    ParseJobResultData,
    ParseJobRetryData,
)


router = APIRouter(tags=["parse-jobs"])


@router.get("/admin/parse-jobs")
def list_parse_jobs(
    _: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
) -> ApiResponse[list[ParseJobListItem]]:
    stmt = select(ParseJob).order_by(ParseJob.created_at.desc())
    if status:
        stmt = stmt.where(ParseJob.status == status)

    jobs = db.scalars(stmt.limit(50)).all()
    return ApiResponse(
        data=[
            ParseJobListItem(
                id=job.id,
                status=job.status,
                entity_type=job.entity_type,
                entity_id=job.entity_id,
                content_category=(job.request_payload_json or {}).get(
                    "content_category"
                ),
                attempt_count=job.attempt_count,
                error_message=job.error_message,
                created_at=job.created_at,
            )
            for job in jobs
        ]
    )


@router.get("/parse-jobs/{job_id}")
def get_parse_job(
    job_id: UUID,
    _: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[ParseJobResultData]:
    job = db.get(ParseJob, job_id)
    if job is None:
        raise NotFoundException("parse job not found")

    return ApiResponse(
        data=ParseJobResultData(
            id=job.id,
            status=job.status,
            entity_type=job.entity_type,
            entity_id=job.entity_id,
            content_category=(job.request_payload_json or {}).get("content_category"),
            result=job.result_json,
            error_message=job.error_message,
            attempt_count=job.attempt_count,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
    )


@router.post("/parse-jobs/{job_id}/retry")
def retry_parse_job(
    job_id: UUID,
    _: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiResponse[ParseJobRetryData]:
    job = db.get(ParseJob, job_id)
    if job is None:
        raise NotFoundException("parse job not found")
    if job.status not in {ParseJobStatus.FAILED.value, ParseJobStatus.PENDING.value}:
        raise ConflictException("only failed or pending jobs can be retried")

    job.status = ParseJobStatus.PENDING.value
    job.error_message = None
    job.attempt_count += 1
    db.commit()

    return ApiResponse(
        data=ParseJobRetryData(
            id=job.id,
            status=job.status,
            attempt_count=job.attempt_count,
        )
    )
