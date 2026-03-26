from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailableException


settings = get_settings()

engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


def verify_database_connection() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
    except SQLAlchemyError as exc:
        raise ServiceUnavailableException("database unavailable") from exc


def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
    except SQLAlchemyError as exc:
        raise ServiceUnavailableException("database unavailable") from exc

    try:
        yield db
    except SQLAlchemyError as exc:
        raise ServiceUnavailableException("database unavailable") from exc
    finally:
        db.close()
