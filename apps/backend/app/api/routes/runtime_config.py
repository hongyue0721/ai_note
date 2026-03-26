from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin_token
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.runtime_config import RuntimeConfigResponse, RuntimeConfigUpdateRequest
from app.services.runtime_config import (
    get_runtime_config_response,
    update_runtime_config,
)


router = APIRouter(tags=["runtime-config"])


@router.get("/admin/runtime-config/models")
def get_runtime_models(
    _: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiResponse[RuntimeConfigResponse]:
    return ApiResponse(data=get_runtime_config_response(db))


@router.put("/admin/runtime-config/models")
def put_runtime_models(
    payload: RuntimeConfigUpdateRequest,
    _: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiResponse[RuntimeConfigResponse]:
    return ApiResponse(data=update_runtime_config(db, payload))
