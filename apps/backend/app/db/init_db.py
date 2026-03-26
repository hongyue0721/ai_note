import logging

from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine
from app.models import AdminUser
from app.services.runtime_config import get_runtime_config_response


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
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS space_key VARCHAR(64) DEFAULT 'default'"
            )
        )
        connection.execute(
            text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_username_key")
        )
        connection.execute(text("DROP INDEX IF EXISTS ix_users_username"))
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_space_username ON users (space_key, username)"
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_users_username ON users (username)")
        )
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS canonical_tags (id UUID PRIMARY KEY, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), name VARCHAR(128) NOT NULL)"
            )
        )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_canonical_tags_name ON canonical_tags (name)"
            )
        )
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS entity_canonical_tags (id UUID PRIMARY KEY, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), entity_type VARCHAR(32) NOT NULL, entity_id UUID NOT NULL, canonical_tag_id UUID NOT NULL, confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0)"
            )
        )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_entity_canonical_tag ON entity_canonical_tags (entity_type, entity_id, canonical_tag_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_entity_canonical_tags_entity ON entity_canonical_tags (entity_type, entity_id)"
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


def ensure_runtime_configs(db: Session) -> None:
    get_runtime_config_response(db)
    logger.info("Runtime model configs ensured")
