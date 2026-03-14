import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging
from app.db.init_db import create_tables, seed_admin_user
from app.db.session import SessionLocal


settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="StarGraph AI competition complete product backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.resolved_uploads_root_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.normalized_uploads_url_base,
    StaticFiles(directory=settings.resolved_uploads_root_dir),
    name="uploads",
)


@app.on_event("startup")
def on_startup() -> None:
    create_tables()
    db: Session = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"code": 5000, "message": "internal error", "data": None},
    )


app.include_router(api_router)
