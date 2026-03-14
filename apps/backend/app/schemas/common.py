from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None


class HealthData(BaseModel):
    status: str = "ok"


class AppMetaData(BaseModel):
    app_name: str
    env: str
    mvp_mode: str = Field(default="competition-demo")
