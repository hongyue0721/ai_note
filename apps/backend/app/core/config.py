from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = Field(default="StarGraph AI", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    admin_jwt_secret: str = Field(default="change-admin-me", alias="ADMIN_JWT_SECRET")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://127.0.0.1:3001,http://146.190.84.189:3000,http://146.190.84.189:3001",
        alias="CORS_ORIGINS",
    )
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/stargraph",
        alias="DATABASE_URL",
    )
    storage_provider: str = Field(default="local", alias="STORAGE_PROVIDER")
    uploads_root_dir: str = Field(default="data/uploads", alias="UPLOADS_ROOT_DIR")
    uploads_url_base: str = Field(default="/uploads", alias="UPLOADS_URL_BASE")
    gemini_model_extract: str = Field(
        default="gemini-2.0-flash", alias="GEMINI_MODEL_EXTRACT"
    )
    gemini_model_solve: str = Field(
        default="gemini-2.0-flash", alias="GEMINI_MODEL_SOLVE"
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", alias="OPENAI_BASE_URL"
    )
    openai_model_classify: str = Field(
        default="gpt-4.1-mini", alias="OPENAI_MODEL_CLASSIFY"
    )
    openai_model_solve: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL_SOLVE")
    openai_timeout_seconds: int = Field(default=60, alias="OPENAI_TIMEOUT_SECONDS")
    backend_log_level: str = Field(default="INFO", alias="BACKEND_LOG_LEVEL")
    seed_admin_username: str = Field(default="admin", alias="SEED_ADMIN_USERNAME")
    seed_admin_password: str = Field(default="admin123456", alias="SEED_ADMIN_PASSWORD")
    seed_admin_display_name: str = Field(
        default="System Admin", alias="SEED_ADMIN_DISPLAY_NAME"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def normalized_uploads_url_base(self) -> str:
        base = self.uploads_url_base.strip() or "/uploads"
        if not base.startswith("/"):
            base = f"/{base}"
        return base.rstrip("/") or "/uploads"

    @property
    def resolved_uploads_root_dir(self) -> Path:
        raw_path = Path(self.uploads_root_dir)
        if raw_path.is_absolute():
            return raw_path
        config_file = Path(__file__).resolve()
        backend_root = config_file.parents[2]
        return backend_root / raw_path


@lru_cache
def get_settings() -> Settings:
    return Settings()
