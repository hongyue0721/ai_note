from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.canonical_tag import CanonicalTag, EntityCanonicalTag
from app.schemas.content import ContentTagData


def _normalize_tag_name(raw: object) -> str:
    return str(raw or "").strip()


def _normalize_confidence(raw: object) -> float:
    try:
        return max(0.0, min(1.0, float(raw)))
    except Exception:
        return 1.0


def sync_entity_canonical_tags(
    db: Session,
    *,
    entity_type: str,
    entity_id: UUID,
    tags: Sequence[dict] | Sequence[ContentTagData] | Sequence[object],
) -> None:
    db.execute(
        delete(EntityCanonicalTag).where(
            EntityCanonicalTag.entity_type == entity_type,
            EntityCanonicalTag.entity_id == entity_id,
        )
    )

    for item in tags:
        payload = item.model_dump(mode="json") if hasattr(item, "model_dump") else item
        if not isinstance(payload, dict):
            continue

        name = _normalize_tag_name(payload.get("name"))
        if not name:
            continue

        canonical = db.scalar(select(CanonicalTag).where(CanonicalTag.name == name))
        if canonical is None:
            canonical = CanonicalTag(name=name)
            db.add(canonical)
            db.flush()

        db.add(
            EntityCanonicalTag(
                entity_type=entity_type,
                entity_id=entity_id,
                canonical_tag_id=canonical.id,
                confidence=_normalize_confidence(payload.get("confidence", 1.0)),
            )
        )


def get_entity_canonical_tags(
    db: Session,
    *,
    entity_type: str,
    entity_id: UUID,
) -> list[ContentTagData]:
    rows = db.execute(
        select(CanonicalTag.name, EntityCanonicalTag.confidence)
        .join(CanonicalTag, CanonicalTag.id == EntityCanonicalTag.canonical_tag_id)
        .where(
            EntityCanonicalTag.entity_type == entity_type,
            EntityCanonicalTag.entity_id == entity_id,
        )
        .order_by(EntityCanonicalTag.confidence.desc(), CanonicalTag.name.asc())
    ).all()
    return [
        ContentTagData(name=str(name), confidence=float(confidence))
        for name, confidence in rows
    ]
