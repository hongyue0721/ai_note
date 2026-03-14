import logging

from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine
from app.models import AdminUser


logger = logging.getLogger(__name__)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE files ADD COLUMN IF NOT EXISTS file_kind VARCHAR(32) DEFAULT 'image'"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE files ADD COLUMN IF NOT EXISTS content_category VARCHAR(32) DEFAULT 'problem'"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE notes ADD COLUMN IF NOT EXISTS category VARCHAR(32) DEFAULT 'note'"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE problems ADD COLUMN IF NOT EXISTS category VARCHAR(32) DEFAULT 'problem'"
            )
        )
    logger.info("Database tables ensured")


def seed_admin_user(db: Session) -> None:
    settings = get_settings()
    existing = db.scalar(
        select(AdminUser).where(AdminUser.username == settings.seed_admin_username)
    )
    if existing is not None:
        logger.info("Admin seed already exists: %s", settings.seed_admin_username)
        return

    admin = AdminUser(
        username=settings.seed_admin_username,
        password_hash=hash_password(settings.seed_admin_password),
        display_name=settings.seed_admin_display_name,
        status="active",
    )
    db.add(admin)
    db.commit()
    logger.info("Admin seed created: %s", settings.seed_admin_username)
