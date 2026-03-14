from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.db.session import get_db
from app.models.note import Note
from app.models.problem import Problem
from app.schemas.common import ApiResponse
from app.schemas.search import SearchItem


router = APIRouter(tags=["search"])


@router.get("/search")
def search_content(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
    q: str = Query(min_length=1),
) -> ApiResponse[list[SearchItem]]:
    keyword = f"%{q}%"
    user_id = UUID(str(token_payload["sub"]))

    problem_items = db.scalars(
        select(Problem)
        .where(
            Problem.user_id == user_id,
            or_(
                Problem.stem_text.ilike(keyword),
                Problem.subject.ilike(keyword),
                Problem.category.ilike(keyword),
            ),
        )
        .limit(10)
    ).all()

    note_items = db.scalars(
        select(Note)
        .where(
            Note.user_id == user_id,
            or_(
                Note.raw_text.ilike(keyword),
                Note.subject.ilike(keyword),
                Note.category.ilike(keyword),
            ),
        )
        .limit(10)
    ).all()

    results: list[SearchItem] = []
    for item in problem_items:
        results.append(
            SearchItem(
                type="problem",
                id=str(item.id),
                title=item.title or "未命名错题",
                snippet=(item.stem_text or "")[:120],
                subject=item.subject,
                category=item.category,
                parse_status=item.parse_status,
            )
        )

    for item in note_items:
        result_type = "document-note" if item.category == "document" else "note"
        results.append(
            SearchItem(
                type=result_type,
                id=str(item.id),
                title=item.title or "未命名笔记",
                snippet=(item.raw_text or "")[:120],
                subject=item.subject,
                category=item.category,
                parse_status=item.parse_status,
            )
        )

    return ApiResponse(data=results)
