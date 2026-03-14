from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin_token, require_user_token
from app.core.constants import ParseJobStatus, ReviewTaskStatus
from app.db.session import get_db
from app.models.note import Note
from app.models.parse_job import ParseJob
from app.models.problem import Problem
from app.models.review_task import ReviewTask
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardData, MonitorOverviewData


router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(
    _: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[DashboardData]:
    today = datetime.now(UTC).date()
    problem_count = (
        db.scalar(
            select(func.count())
            .select_from(Problem)
            .where(func.date(Problem.created_at) == today)
        )
        or 0
    )
    note_count = (
        db.scalar(
            select(func.count())
            .select_from(Note)
            .where(func.date(Note.created_at) == today)
        )
        or 0
    )
    pending_review_count = (
        db.scalar(
            select(func.count())
            .select_from(ReviewTask)
            .where(ReviewTask.status == ReviewTaskStatus.PENDING.value)
        )
        or 0
    )
    pending_parse_count = (
        db.scalar(
            select(func.count())
            .select_from(ParseJob)
            .where(ParseJob.status == ParseJobStatus.PENDING.value)
        )
        or 0
    )
    failed_parse_count = (
        db.scalar(
            select(func.count())
            .select_from(ParseJob)
            .where(ParseJob.status == ParseJobStatus.FAILED.value)
        )
        or 0
    )

    return ApiResponse(
        data=DashboardData(
            today_problem_count=problem_count,
            today_note_count=note_count,
            pending_review_count=pending_review_count,
            pending_parse_job_count=pending_parse_count,
            failed_parse_job_count=failed_parse_count,
        )
    )


@router.get("/admin/monitor/overview")
def get_monitor_overview(
    _: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiResponse[MonitorOverviewData]:
    total = db.scalar(select(func.count()).select_from(ParseJob)) or 0
    pending = (
        db.scalar(
            select(func.count())
            .select_from(ParseJob)
            .where(ParseJob.status == ParseJobStatus.PENDING.value)
        )
        or 0
    )
    failed = (
        db.scalar(
            select(func.count())
            .select_from(ParseJob)
            .where(ParseJob.status == ParseJobStatus.FAILED.value)
        )
        or 0
    )
    review_pending = (
        db.scalar(
            select(func.count())
            .select_from(ReviewTask)
            .where(ReviewTask.status == ReviewTaskStatus.PENDING.value)
        )
        or 0
    )

    latest_errors = db.scalars(
        select(ParseJob.error_message)
        .where(ParseJob.error_message.is_not(None))
        .order_by(ParseJob.updated_at.desc())
        .limit(5)
    ).all()

    return ApiResponse(
        data=MonitorOverviewData(
            service_status="ok",
            parse_job_total=total,
            parse_job_pending=pending,
            parse_job_failed=failed,
            review_task_pending=review_pending,
            latest_error_messages=[msg for msg in latest_errors if msg],
        )
    )
