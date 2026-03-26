from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.problem import Problem
from app.schemas.common import ApiResponse
from app.schemas.content import ProblemDetailData, ProblemListItem, ProblemUpdateRequest


router = APIRouter(tags=["problems"])


@router.get("/problems")
def list_problems(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
    subject: str | None = Query(default=None),
    category: str | None = Query(default=None),
) -> ApiResponse[list[ProblemListItem]]:
    user_id = UUID(str(token_payload["sub"]))
    stmt = (
        select(Problem)
        .where(Problem.user_id == user_id)
        .order_by(Problem.created_at.desc())
    )
    if subject:
        stmt = stmt.where(Problem.subject == subject)
    if category:
        stmt = stmt.where(Problem.category == category)

    items = db.scalars(stmt).all()
    return ApiResponse(
        data=[
            ProblemListItem(
                id=item.id,
                title=item.title,
                subject=item.subject,
                category=item.category,
                parse_status=item.parse_status,
                stem_text=item.stem_text,
                created_at=item.created_at,
            )
            for item in items
        ]
    )


@router.get("/problems/{problem_id}")
def get_problem(
    problem_id: UUID,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[ProblemDetailData]:
    item = db.get(Problem, problem_id)
    if item is None:
        raise NotFoundException("problem not found")
    if item.user_id != UUID(str(token_payload["sub"])):
        raise NotFoundException("problem not found")

    return ApiResponse(
        data=ProblemDetailData(
            id=item.id,
            title=item.title,
            subject=item.subject,
            category=item.category,
            parse_status=item.parse_status,
            stem_text=item.stem_text,
            normalized_stem=item.normalized_stem,
            answer_text=item.answer_text,
            explanation_text=item.explanation_text,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
    )


@router.patch("/problems/{problem_id}")
def update_problem(
    problem_id: UUID,
    payload: ProblemUpdateRequest,
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[ProblemDetailData]:
    item = db.get(Problem, problem_id)
    if item is None:
        raise NotFoundException("problem not found")
    if item.user_id != UUID(str(token_payload["sub"])):
        raise NotFoundException("problem not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)

    return ApiResponse(
        data=ProblemDetailData(
            id=item.id,
            title=item.title,
            subject=item.subject,
            category=item.category,
            parse_status=item.parse_status,
            stem_text=item.stem_text,
            normalized_stem=item.normalized_stem,
            answer_text=item.answer_text,
            explanation_text=item.explanation_text,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
    )
