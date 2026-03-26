from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.runtime_config import RuntimeConfig
from app.schemas.runtime_config import (
    RuntimeConfigResponse,
    RuntimeConfigItem,
    RuntimeConfigUpdateRequest,
)


def _default_item(scope: str) -> RuntimeConfigItem:
    settings = get_settings()
    model_name = (
        settings.openai_model_solve
        if scope == "solve"
        else settings.openai_model_classify
    )
    return RuntimeConfigItem(
        scope=scope,
        vendor="openai-compatible",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key or "",
        model_name=model_name,
    )


def _get_or_create_scope(db: Session, scope: str) -> RuntimeConfig:
    record = db.scalar(select(RuntimeConfig).where(RuntimeConfig.scope == scope))
    if record is not None:
        return record
    default = _default_item(scope)
    record = RuntimeConfig(
        scope=scope,
        vendor=default.vendor,
        base_url=default.base_url,
        api_key=default.api_key,
        model_name=default.model_name,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_runtime_config_response(db: Session) -> RuntimeConfigResponse:
    solve = _get_or_create_scope(db, "solve")
    classify = _get_or_create_scope(db, "classify")
    return RuntimeConfigResponse(
        solve=RuntimeConfigItem(
            scope="solve",
            vendor=solve.vendor,
            base_url=solve.base_url,
            api_key=solve.api_key,
            model_name=solve.model_name,
        ),
        classify=RuntimeConfigItem(
            scope="classify",
            vendor=classify.vendor,
            base_url=classify.base_url,
            api_key=classify.api_key,
            model_name=classify.model_name,
        ),
    )


def update_runtime_config(
    db: Session, payload: RuntimeConfigUpdateRequest
) -> RuntimeConfigResponse:
    solve = _get_or_create_scope(db, "solve")
    classify = _get_or_create_scope(db, "classify")
    solve.vendor = payload.solve.vendor
    solve.base_url = payload.solve.base_url
    solve.api_key = payload.solve.api_key
    solve.model_name = payload.solve.model_name
    classify.vendor = payload.classify.vendor
    classify.base_url = payload.classify.base_url
    classify.api_key = payload.classify.api_key
    classify.model_name = payload.classify.model_name
    db.commit()
    db.refresh(solve)
    db.refresh(classify)
    return get_runtime_config_response(db)


def get_runtime_scope_config(db: Session, scope: str) -> RuntimeConfigItem:
    record = _get_or_create_scope(db, scope)
    return RuntimeConfigItem(
        scope=scope,
        vendor=record.vendor,
        base_url=record.base_url,
        api_key=record.api_key,
        model_name=record.model_name,
    )
