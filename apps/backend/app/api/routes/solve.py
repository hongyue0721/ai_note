from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_user_token
from app.core.exceptions import AppException
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.solve import SolveRequest, SolveResultData
from app.services.solver import solve_with_ai


router = APIRouter(tags=["solve"])


@router.post("/solve")
def solve_question(
    payload: SolveRequest,
    _: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[SolveResultData]:
    if not payload.allow_ai_fallback:
        raise AppException(
            code=4006,
            message="allow_ai_fallback=false is not supported because the current solve pipeline is AI-only",
            status_code=400,
        )
    result = solve_with_ai(
        question_text=payload.question_text,
        subject=payload.subject,
        db=db,
    )
    return ApiResponse(data=result)
