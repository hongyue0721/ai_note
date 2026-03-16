from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin_token, require_user_token
from app.core.constants import ParseJobStatus, ReviewTaskStatus
from app.db.session import get_db
from app.models.note import Note
from app.models.parse_job import ParseJob
from app.models.problem import Problem
from app.models.review_task import ReviewTask
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardData, MonitorOverviewData, UserNoteStatItem


router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[DashboardData]:
    user_id = str(token_payload["sub"])
    today = datetime.now(UTC).date()
    problem_count = (
        db.scalar(
            select(func.count())
            .select_from(Problem)
            .where(Problem.user_id == user_id, func.date(Problem.created_at) == today)
        )
        or 0
    )
    note_count = (
        db.scalar(
            select(func.count())
            .select_from(Note)
            .where(Note.user_id == user_id, func.date(Note.created_at) == today)
        )
        or 0
    )
    pending_review_count = (
        db.scalar(
            select(func.count())
            .select_from(ReviewTask)
            .where(
                ReviewTask.user_id == user_id,
                ReviewTask.status == ReviewTaskStatus.PENDING.value,
            )
        )
        or 0
    )
    pending_parse_count = (
        db.scalar(
            select(func.count())
            .select_from(ParseJob)
            .where(
                ParseJob.user_id == user_id,
                ParseJob.status == ParseJobStatus.PENDING.value,
            )
        )
        or 0
    )
    failed_parse_count = (
        db.scalar(
            select(func.count())
            .select_from(ParseJob)
            .where(
                ParseJob.user_id == user_id,
                ParseJob.status == ParseJobStatus.FAILED.value,
            )
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
    request: Request,
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
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    total_notes = db.scalar(select(func.count()).select_from(Note)) or 0

    user_note_rows = db.execute(
        select(
            User.username,
            User.space_key,
            func.count(Note.id).label("note_count"),
        )
        .select_from(User)
        .outerjoin(Note, Note.user_id == User.id)
        .group_by(User.id, User.username, User.space_key, User.created_at)
        .order_by(func.count(Note.id).desc(), User.created_at.desc())
        .limit(20)
    ).all()

    latest_errors = db.scalars(
        select(ParseJob.error_message)
        .where(ParseJob.error_message.is_not(None))
        .order_by(ParseJob.updated_at.desc())
        .limit(5)
    ).all()

    metrics = getattr(request.app.state, "api_metrics", None)
    request_count = int(metrics["count"]) if isinstance(metrics, dict) else total
    avg_response_ms = (
        round(float(metrics["total_ms"]) / request_count, 1)
        if isinstance(metrics, dict) and request_count
        else 0.0
    )

    return ApiResponse(
        data=MonitorOverviewData(
            service_status="ok",
            parse_job_total=total,
            parse_job_pending=pending,
            parse_job_failed=failed,
            latest_error_messages=[msg for msg in latest_errors if msg],
            api_request_count=request_count,
            api_avg_response_ms=avg_response_ms,
            total_user_count=total_users,
            total_note_count=total_notes,
            user_note_stats=[
                UserNoteStatItem(
                    username=row.username,
                    space_key=row.space_key,
                    note_count=int(row.note_count or 0),
                )
                for row in user_note_rows
            ],
        )
    )
