from fastapi import APIRouter

from app.schemas.common import ApiResponse, HealthData


router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthcheck() -> ApiResponse[HealthData]:
    return ApiResponse(data=HealthData())
