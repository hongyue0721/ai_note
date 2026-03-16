from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ParseJobStatus
from app.core.config import get_settings
from app.models.note import Note
from app.models.parse_job import ParseJob
from app.models.problem import Problem
from app.services.classifier import classify_content


def load_next_pending_parse_job(db: Session) -> ParseJob | None:
    stmt = (
        select(ParseJob)
        .where(ParseJob.status == ParseJobStatus.PENDING.value)
        .order_by(ParseJob.created_at.asc())
        .limit(1)
    )
    return db.scalar(stmt)


def _build_mock_result(job: ParseJob, entity_text: str | None) -> dict:
    base_text = entity_text or "未提供文本，基于上传内容生成占位解析结果"
    request_payload = job.request_payload_json or {}
    content_category = request_payload.get("content_category", job.entity_type)
    file_kind = "document" if content_category == "document" else "image"
    if len(base_text) > 40:
        title = base_text[:40]
    else:
        title = base_text

    low_confidence = "难" in base_text or entity_text is None
    confidence = 0.62 if low_confidence else 0.91
    candidates = []
    if "方程" in base_text or entity_text is None:
        candidates.append(
            {
                "name": "一元二次方程",
                "confidence": confidence,
            }
        )

    return {
        "title": title,
        "content_category": content_category,
        "file_kind": file_kind,
        "raw_text": base_text,
        "normalized_text": base_text.strip(),
        "knowledge_candidates": candidates,
        "confidence": confidence,
        "needs_review": False,
        "review_reason": "",
    }


def _get_entity_text(db: Session, job: ParseJob) -> str | None:
    if job.entity_type == "note":
        note = db.get(Note, job.entity_id)
        return note.raw_text if note else None

    problem = db.get(Problem, job.entity_id)
    return problem.stem_text if problem else None


def _set_entity_parse_status(db: Session, job: ParseJob, status: str) -> None:
    if job.entity_type == "note":
        note = db.get(Note, job.entity_id)
        if note is not None:
            note.parse_status = status
        return

    problem = db.get(Problem, job.entity_id)
    if problem is not None:
        problem.parse_status = status


def process_parse_job(db: Session, job: ParseJob) -> ParseJob:
    job.status = ParseJobStatus.RUNNING.value
    _set_entity_parse_status(db, job, ParseJobStatus.RUNNING.value)
    job.started_at = datetime.now(UTC)
    job.attempt_count += 1
    db.commit()
    db.refresh(job)

    try:
        entity_text = _get_entity_text(db, job)
        request_payload = job.request_payload_json or {}
        file_kind = (
            "document"
            if request_payload.get("content_category") == "document"
            else "image"
        )

        if get_settings().openai_api_key:
            classification, model_name = classify_content(
                text_content=entity_text or "未提供正文内容",
                file_kind=file_kind,
                content_category=str(
                    request_payload.get("content_category", job.entity_type)
                ),
                db=db,
            )
            result = classification.model_dump(mode="json")
            job.llm_model = model_name
        else:
            result = _build_mock_result(job, entity_text)

        job.result_json = result
        job.status = ParseJobStatus.SUCCESS.value
        _set_entity_parse_status(db, job, ParseJobStatus.SUCCESS.value)
        job.error_message = None
        job.finished_at = datetime.now(UTC)

        db.commit()
        db.refresh(job)
        return job
    except Exception as exc:
        job.status = ParseJobStatus.FAILED.value
        _set_entity_parse_status(db, job, ParseJobStatus.FAILED.value)
        job.error_message = str(exc)
        job.finished_at = datetime.now(UTC)
        db.commit()
        db.refresh(job)
        return job
