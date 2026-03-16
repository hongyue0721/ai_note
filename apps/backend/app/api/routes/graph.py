from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.db.session import get_db
from app.models.note import Note
from app.models.parse_job import ParseJob
from app.models.problem import Problem
from app.schemas.common import ApiResponse
from app.schemas.graph import GraphNode, GraphOverviewData, WeakTagItem


router = APIRouter(tags=["graph"])


@router.get("/graph/overview")
def get_graph_overview(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[GraphOverviewData]:
    user_id = UUID(str(token_payload["sub"]))
    jobs = db.scalars(
        select(ParseJob)
        .where(ParseJob.user_id == user_id, ParseJob.result_json.is_not(None))
        .order_by(ParseJob.created_at.desc())
        .limit(100)
    ).all()
    note_ids = {
        item[0]
        for item in db.execute(select(Note.id).where(Note.user_id == user_id)).all()
    }
    problem_ids = {
        item[0]
        for item in db.execute(
            select(Problem.id).where(Problem.user_id == user_id)
        ).all()
    }
    weights: dict[str, float] = {}

    for job in jobs:
        if job.entity_type == "note" and job.entity_id not in note_ids:
            continue
        if job.entity_type == "problem" and job.entity_id not in problem_ids:
            continue
        result = job.result_json or {}
        for item in result.get("knowledge_candidates", []):
            name = item.get("name")
            confidence = float(item.get("confidence", 0))
            if not name:
                continue
            weights[name] = weights.get(name, 0) + confidence

    nodes = [
        GraphNode(name=name, weight=round(weight, 2))
        for name, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True)[
            :12
        ]
    ]
    total_problems = (
        db.scalar(
            select(func.count()).select_from(Problem).where(Problem.user_id == user_id)
        )
        or 0
    )
    total_notes = (
        db.scalar(select(func.count()).select_from(Note).where(Note.user_id == user_id))
        or 0
    )

    return ApiResponse(
        data=GraphOverviewData(
            nodes=nodes,
            total_problems=total_problems,
            total_notes=total_notes,
        )
    )


@router.get("/graph/weak-tags")
def get_weak_tags(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[list[WeakTagItem]]:
    user_id = UUID(str(token_payload["sub"]))
    jobs = db.scalars(
        select(ParseJob)
        .where(ParseJob.user_id == user_id, ParseJob.result_json.is_not(None))
        .order_by(ParseJob.created_at.desc())
        .limit(100)
    ).all()
    note_ids = {
        item[0]
        for item in db.execute(select(Note.id).where(Note.user_id == user_id)).all()
    }
    problem_ids = {
        item[0]
        for item in db.execute(
            select(Problem.id).where(Problem.user_id == user_id)
        ).all()
    }
    weights: dict[str, float] = {}

    for job in jobs:
        if job.entity_type == "note" and job.entity_id not in note_ids:
            continue
        if job.entity_type == "problem" and job.entity_id not in problem_ids:
            continue
        result = job.result_json or {}
        for item in result.get("knowledge_candidates", []):
            name = item.get("name")
            confidence = float(item.get("confidence", 0))
            if not name:
                continue
            score = 1 - confidence
            weights[name] = weights.get(name, 0) + score

    tags = [
        WeakTagItem(name=name, score=round(score, 2))
        for name, score in sorted(weights.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
    ]
    return ApiResponse(data=tags)
