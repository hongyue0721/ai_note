from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.db.session import get_db
from app.models.note import Note
from app.models.problem import Problem
from app.schemas.common import ApiResponse
from app.schemas.search import SearchItem, SearchResponseData


router = APIRouter(tags=["search"])


@router.get("/search")
def search_content(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    type: str | None = Query(default=None),
    subject: str | None = Query(default=None),
    category: str | None = Query(default=None),
) -> ApiResponse[SearchResponseData]:
    keyword = f"%{q}%"
    user_id = UUID(str(token_payload["sub"]))

    normalized_type = (type or "").strip().lower()
    normalized_subject = (subject or "").strip()
    normalized_category = (category or "").strip()

    problem_filter = [
        Problem.user_id == user_id,
        or_(
            Problem.stem_text.ilike(keyword),
            Problem.subject.ilike(keyword),
            Problem.category.ilike(keyword),
        ),
    ]
    note_filter = [
        Note.user_id == user_id,
        or_(
            Note.raw_text.ilike(keyword),
            Note.subject.ilike(keyword),
            Note.category.ilike(keyword),
        ),
    ]

    if normalized_subject:
        problem_filter.append(Problem.subject == normalized_subject)
        note_filter.append(Note.subject == normalized_subject)

    if normalized_category:
        problem_filter.append(Problem.category == normalized_category)
        note_filter.append(Note.category == normalized_category)

    include_problems = normalized_type not in {"note", "document-note"}
    include_notes = normalized_type not in {"problem"}

    total_problems = (
        db.scalar(select(func.count()).select_from(Problem).where(*problem_filter))
        if include_problems
        else 0
    ) or 0
    total_notes = (
        db.scalar(select(func.count()).select_from(Note).where(*note_filter))
        if include_notes
        else 0
    ) or 0
    total = total_problems + total_notes

    problem_items = (
        db.scalars(
            select(Problem)
            .where(*problem_filter)
            .order_by(Problem.created_at.desc())
            .limit(limit + offset)
        ).all()
        if include_problems
        else []
    )

    note_items = (
        db.scalars(
            select(Note)
            .where(*note_filter)
            .order_by(Note.created_at.desc())
            .limit(limit + offset)
        ).all()
        if include_notes
        else []
    )

    merged_results: list[tuple[str, SearchItem]] = []
    for item in problem_items:
        merged_results.append(
            (
                item.created_at.isoformat(),
                SearchItem(
                    type="problem",
                    id=str(item.id),
                    title=item.title or "未命名错题",
                    snippet=(item.stem_text or "")[:120],
                    subject=item.subject,
                    category=item.category,
                    parse_status=item.parse_status,
                ),
            )
        )

    for item in note_items:
        result_type = "document-note" if item.category == "document" else "note"
        merged_results.append(
            (
                item.created_at.isoformat(),
                SearchItem(
                    type=result_type,
                    id=str(item.id),
                    title=item.title or "未命名笔记",
                    snippet=(item.raw_text or "")[:120],
                    subject=item.subject,
                    category=item.category,
                    parse_status=item.parse_status,
                ),
            )
        )

    merged_results.sort(key=lambda pair: pair[0], reverse=True)
    paged_items = [item for _, item in merged_results[offset : offset + limit]]

    return ApiResponse(
        data=SearchResponseData(
            items=paged_items,
            total=total,
            limit=limit,
            offset=offset,
        )
    )
