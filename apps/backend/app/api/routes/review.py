from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin_token
from app.core.constants import ReviewTaskStatus
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.review_task import ReviewTask
from app.schemas.common import ApiResponse
from app.schemas.review import ReviewDecisionData, ReviewDecisionRequest, ReviewTaskItem


router = APIRouter(tags=["review"])


@router.get("/review/tasks")
def list_review_tasks(
    _: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
    task_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
) -> ApiResponse[list[ReviewTaskItem]]:
    stmt = select(ReviewTask).order_by(ReviewTask.created_at.desc())
    if task_type:
        stmt = stmt.where(ReviewTask.task_type == task_type)
    if status:
        stmt = stmt.where(ReviewTask.status == status)
    if entity_type:
        stmt = stmt.where(ReviewTask.entity_type == entity_type)

    items = db.scalars(stmt).all()
    return ApiResponse(
        data=[
            ReviewTaskItem(
                id=item.id,
                task_type=item.task_type,
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                status=item.status,
                payload_json=item.payload_json,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]
    )


@router.post("/review/tasks/{task_id}/decision")
def decide_review_task(
    task_id: UUID,
    payload: ReviewDecisionRequest,
    _: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiResponse[ReviewDecisionData]:
    task = db.get(ReviewTask, task_id)
    if task is None:
        raise NotFoundException("review task not found")

    if payload.action == "approve":
        task.status = ReviewTaskStatus.APPROVED.value
    elif payload.action == "reject":
        task.status = ReviewTaskStatus.REJECTED.value
    else:
        task.status = ReviewTaskStatus.FIXED.value

    if task.payload_json is None:
        task.payload_json = {}
    task.payload_json["decision"] = payload.action
    task.payload_json["edited_tags"] = payload.edited_tags
    db.commit()

    return ApiResponse(data=ReviewDecisionData(id=task.id, status=task.status))
