from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import ApiResponse, AppMetaData


router = APIRouter(tags=["meta"])


@router.get("/meta/app")
def app_meta() -> ApiResponse[AppMetaData]:
    settings = get_settings()
    return ApiResponse(
        data=AppMetaData(
            app_name=settings.app_name,
            env=settings.app_env,
        )
    )
