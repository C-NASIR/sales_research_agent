from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ActivityEvent
from app.utils.ids import new_id
from app.utils.timestamps import utc_now


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
    return event


def list_events_for_campaign(db: Session, campaign_id: str) -> list[ActivityEvent]:
    statement = (
        select(ActivityEvent)
        .where(ActivityEvent.campaign_id == campaign_id)
        .order_by(ActivityEvent.created_at.asc())
    )
    return list(db.scalars(statement).all())
