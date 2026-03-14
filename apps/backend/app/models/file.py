import uuid

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class FileRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "files"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    object_key: Mapped[str] = mapped_column(String(255), unique=True)
    storage_provider: Mapped[str] = mapped_column(String(32))
    bucket_name: Mapped[str] = mapped_column(String(128))
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(128))
    file_kind: Mapped[str] = mapped_column(String(32), default="image")
    content_category: Mapped[str] = mapped_column(String(32), default="problem")
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), default="upload")
    upload_status: Mapped[str] = mapped_column(
        String(32), default="pending", index=True
    )
