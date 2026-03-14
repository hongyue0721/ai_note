from fastapi import APIRouter, Depends

from app.api.deps.auth import require_user_token
from app.schemas.common import ApiResponse
from app.schemas.solve import SolveRequest, SolveResultData
from app.services.solver import solve_with_ai


router = APIRouter(tags=["solve"])


@router.post("/solve")
def solve_question(
    payload: SolveRequest,
    _: dict[str, object] = Depends(require_user_token),
) -> ApiResponse[SolveResultData]:
    result = solve_with_ai(
        question_text=payload.question_text,
        subject=payload.subject,
    )
    return ApiResponse(data=result)
