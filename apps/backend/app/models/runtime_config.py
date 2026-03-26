from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RuntimeConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "runtime_configs"

    scope: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    vendor: Mapped[str] = mapped_column(String(64), default="openai-compatible")
    base_url: Mapped[str] = mapped_column(Text, default="")
    api_key: Mapped[str] = mapped_column(Text, default="")
    model_name: Mapped[str] = mapped_column(String(128), default="")
