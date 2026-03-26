import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CanonicalTag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "canonical_tags"
    __table_args__ = (UniqueConstraint("name", name="uq_canonical_tags_name"),)

    name: Mapped[str] = mapped_column(String(128), index=True)


class EntityCanonicalTag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "entity_canonical_tags"
    __table_args__ = (
        UniqueConstraint(
            "entity_type",
            "entity_id",
            "canonical_tag_id",
            name="uq_entity_canonical_tag",
        ),
    )

    entity_type: Mapped[str] = mapped_column(String(32), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    canonical_tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    confidence: Mapped[float] = mapped_column(default=1.0)
