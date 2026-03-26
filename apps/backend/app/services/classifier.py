import json
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.schemas.classifier import ClassificationResult
from app.services.llm_client import OpenAIClient
from app.services.runtime_config import get_runtime_scope_config


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "classify_prompt.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _extract_confidence(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _fallback_classification(
    *, text_content: str, file_kind: str, content_category: str
) -> ClassificationResult:
    normalized = " ".join(text_content.split()) or "未提供正文内容"
    base_title = normalized[:24] if normalized else "未命名内容"
    subject = "math" if "方程" in normalized else "general"
    candidates: list[dict[str, object]] = []
    if "方程" in normalized:
        candidates.append({"name": "方程求解", "confidence": 0.8})

    confidence_values = [
        _extract_confidence(item.get("confidence", 0.0)) for item in candidates
    ]
    confidence = min(confidence_values) if confidence_values else 0.0

    return ClassificationResult.model_validate(
        {
            "entity_type": "problem" if content_category == "problem" else "note",
            "content_category": content_category,
            "subject": subject,
            "title": base_title,
            "normalized_text": normalized,
            "knowledge_candidates": candidates,
            "confidence": confidence,
            "needs_review": False,
            "review_reason": "",
        }
    )


def classify_content(
    *,
    text_content: str,
    file_kind: str,
    content_category: str,
    db: Session,
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
    llm_client: OpenAIClient | None = None,
) -> tuple[ClassificationResult, str]:
    runtime_config = get_runtime_scope_config(db, "classify")
    client = llm_client or OpenAIClient(runtime_config=runtime_config)

    user_prompt = (
        f"file_kind={file_kind}\n"
        f"content_category={content_category}\n"
        f"text_content={text_content}\n"
    )

    if image_bytes is not None and image_mime_type:
        try:
            response = client.chat_json_with_image(
                model=runtime_config.model_name,
                system_prompt=_load_prompt(),
                user_prompt=user_prompt,
                image_bytes=image_bytes,
                image_mime_type=image_mime_type,
            )
        except Exception:
            return _fallback_classification(
                text_content=text_content,
                file_kind=file_kind,
                content_category=content_category,
            ), "fallback-local"
    else:
        try:
            response = client.chat_json(
                model=runtime_config.model_name,
                system_prompt=_load_prompt(),
                user_prompt=user_prompt,
            )
        except Exception:
            return _fallback_classification(
                text_content=text_content,
                file_kind=file_kind,
                content_category=content_category,
            ), "fallback-local"

    try:
        payload = json.loads(response.content)
    except json.JSONDecodeError as exc:
        return _fallback_classification(
            text_content=text_content,
            file_kind=file_kind,
            content_category=content_category,
        ), "fallback-local"

    try:
        result = ClassificationResult.model_validate(payload)
        result.needs_review = False
        result.review_reason = ""
        return result, response.model
    except ValidationError as exc:
        return _fallback_classification(
            text_content=text_content,
            file_kind=file_kind,
            content_category=content_category,
        ), "fallback-local"
