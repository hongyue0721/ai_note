import json
from pathlib import Path

from pydantic import ValidationError

from app.core.exceptions import AppException
from app.core.config import get_settings
from app.schemas.classifier import ClassificationResult
from app.services.llm_client import OpenAIClient


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "classify_prompt.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def classify_content(
    *,
    text_content: str,
    file_kind: str,
    content_category: str,
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
    llm_client: OpenAIClient | None = None,
) -> tuple[ClassificationResult, str]:
    settings = get_settings()
    client = llm_client or OpenAIClient()

    user_prompt = (
        f"file_kind={file_kind}\n"
        f"content_category={content_category}\n"
        f"text_content={text_content}\n"
    )

    if image_bytes is not None and image_mime_type:
        response = client.chat_json_with_image(
            model=settings.openai_model_classify,
            system_prompt=_load_prompt(),
            user_prompt=user_prompt,
            image_bytes=image_bytes,
            image_mime_type=image_mime_type,
        )
    else:
        response = client.chat_json(
            model=settings.openai_model_classify,
            system_prompt=_load_prompt(),
            user_prompt=user_prompt,
        )

    try:
        payload = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise AppException(
            code=5007,
            message=f"classifier returned invalid json: {exc}",
            status_code=502,
        ) from exc

    try:
        return ClassificationResult.model_validate(payload), response.model
    except ValidationError as exc:
        raise AppException(
            code=5005,
            message=f"classifier returned incompatible schema: {exc}",
            status_code=502,
        ) from exc
