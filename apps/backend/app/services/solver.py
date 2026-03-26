import json
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.schemas.solve import SolveResultData
from app.services.llm_client import OpenAIClient
from app.services.runtime_config import get_runtime_scope_config


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "solve_prompt.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _ensure_list_of_strings(value: object, *, default: list[str]) -> list[str]:
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return items or default
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return default


def _normalize_solve_payload(
    payload: dict[str, object], subject: str | None
) -> dict[str, object]:
    normalized = dict(payload)

    normalized["subject"] = (
        str(normalized.get("subject") or subject or "general").strip() or "general"
    )

    normalized["question_type"] = (
        str(
            normalized.get("question_type")
            or normalized.get("type")
            or normalized.get("problem_type")
            or "unknown"
        ).strip()
        or "unknown"
    )

    normalized["final_answer"] = (
        str(
            normalized.get("final_answer")
            or normalized.get("answer")
            or normalized.get("result")
            or "未提供"
        ).strip()
        or "未提供"
    )

    normalized["solution_steps"] = _ensure_list_of_strings(
        normalized.get("solution_steps") or normalized.get("steps"),
        default=["模型未提供分步过程，请结合最终答案人工复核。"],
    )

    normalized["knowledge_points"] = _ensure_list_of_strings(
        normalized.get("knowledge_points")
        or normalized.get("knowledge")
        or normalized.get("concepts"),
        default=[],
    )

    confidence = normalized.get("confidence", 0.5)
    if isinstance(confidence, (int, float, str)):
        try:
            normalized["confidence"] = max(0.0, min(1.0, float(confidence)))
        except Exception:
            normalized["confidence"] = 0.5
    else:
        normalized["confidence"] = 0.5

    warnings = _ensure_list_of_strings(
        normalized.get("warnings") or normalized.get("warning"),
        default=["以下为 AI 参考解析，请以老师讲解或教材为准。"],
    )
    if not any(
        "AI" in item or "人工" in item or "参考解析" in item for item in warnings
    ):
        warnings.append("以下为 AI 参考解析，请以老师讲解或教材为准。")
    normalized["warnings"] = warnings

    return normalized


def solve_with_ai(
    *, question_text: str, subject: str | None, db: Session
) -> SolveResultData:
    runtime_config = get_runtime_scope_config(db, "solve")
    client = OpenAIClient(runtime_config=runtime_config)

    user_prompt = f"subject={subject or 'unknown'}\nquestion_text={question_text}\n"
    response = client.chat_json(
        model=runtime_config.model_name,
        system_prompt=_load_prompt(),
        user_prompt=user_prompt,
    )

    try:
        payload = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise AppException(
            code=5008,
            message=f"solve returned invalid json: {exc}",
            status_code=502,
        ) from exc

    payload = _normalize_solve_payload(payload, subject)
    payload["model"] = response.model
    try:
        return SolveResultData.model_validate(payload)
    except ValidationError as exc:
        raise AppException(
            code=5006,
            message=f"solve returned incompatible schema: {exc}",
            status_code=502,
        ) from exc
