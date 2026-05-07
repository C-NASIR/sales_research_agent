from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ActivityEvent
from app.utils.ids import new_id
from app.utils.timestamps import utc_now

logger = logging.getLogger(__name__)

IMPORTANT_EVENT_LEVELS = {
    "campaign_created": logging.INFO,
    "csv_upload_completed": logging.INFO,
    "csv_upload_failed": logging.WARNING,
    "run_started": logging.INFO,
    "run_completed": logging.INFO,
    "run_failed": logging.WARNING,
    "account_failed": logging.WARNING,
    "exports_created": logging.INFO,
    "export_failed": logging.WARNING,
}

SAFE_PAYLOAD_KEYS = {
    "account_id",
    "company_name",
    "created_accounts",
    "duplicate_rows",
    "error",
    "export_count",
    "fields_updated",
    "filename",
    "include_review_statuses",
    "invalid_rows",
    "quality_status",
    "review_status",
    "status",
    "valid_rows",
    "workspace_path",
}


def record_event(
    db: Session,
    campaign_id: str,
    type: str,
    message: str,
    payload: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> ActivityEvent:
    event = ActivityEvent(
        id=new_id("event"),
        campaign_id=campaign_id,
        run_id=run_id,
        type=type,
        message=message,
        payload=payload,
        created_at=utc_now(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    _log_important_event(event)
    return event


def list_events_for_campaign(db: Session, campaign_id: str) -> list[ActivityEvent]:
    statement = (
        select(ActivityEvent)
        .where(ActivityEvent.campaign_id == campaign_id)
        .order_by(ActivityEvent.created_at.asc())
    )
    return list(db.scalars(statement).all())


def _log_important_event(event: ActivityEvent) -> None:
    level = IMPORTANT_EVENT_LEVELS.get(event.type)
    if level is None:
        return

    logger.log(
        level,
        "event=%s campaign_id=%s run_id=%s message=%s payload=%s",
        event.type,
        event.campaign_id,
        event.run_id,
        event.message,
        _sanitize_payload(event.payload),
    )


def _sanitize_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None

    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        if key not in SAFE_PAYLOAD_KEYS:
            continue
        if isinstance(value, str):
            sanitized[key] = value[:300]
        elif isinstance(value, list):
            sanitized[key] = value[:10]
        else:
            sanitized[key] = value
    return sanitized or None
