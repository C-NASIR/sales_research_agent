from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OutreachDraft
from app.schemas.outreach import OutreachDraftUpdate
from app.schemas.review import REVIEW_STATUSES
from app.services import account_service, event_service
from app.services.result_service import update_outreach_quality_status
from app.tools.quality_review_tools import review_outreach_quality
from app.utils.timestamps import utc_now
from app.workspace import paths, readers, writers


def validate_review_status(review_status: str) -> str:
    normalized = review_status.strip()
    if normalized not in REVIEW_STATUSES:
        raise ValueError("Invalid review status.")
    return normalized


def update_account_review_status(
    db: Session,
    campaign_id: str,
    account_id: str,
    review_status: str,
) -> dict | None:
    account = account_service.get_account(db, campaign_id, account_id)
    if account is None:
        return None

    normalized_status = validate_review_status(review_status)
    account.review_status = normalized_status
    account.updated_at = utc_now()
    db.commit()
    db.refresh(account)

    event_service.record_event(
      db,
      campaign_id,
      "account_review_updated",
      "Account review status updated",
      {
          "account_id": account.id,
          "company_name": account.company_name,
          "review_status": account.review_status,
      },
    )

    return {
        "account_id": account.id,
        "campaign_id": account.campaign_id,
        "review_status": account.review_status,
        "updated_at": account.updated_at,
    }


def update_outreach_draft(
    db: Session,
    campaign_id: str,
    account_id: str,
    update: OutreachDraftUpdate,
) -> OutreachDraft | None:
    account = account_service.get_account(db, campaign_id, account_id)
    if account is None:
        return None

    payload = update.model_dump(exclude_unset=True)
    _validate_outreach_draft_update(payload)

    draft = db.scalars(select(OutreachDraft).where(OutreachDraft.account_id == account_id)).first()
    if draft is None:
        return None

    for field, value in payload.items():
        setattr(draft, field, value)

    draft.updated_at = utc_now()
    db.commit()
    db.refresh(draft)

    draft_payload = _build_outreach_workspace_payload(campaign_id, account_id, account.company_name, account.domain, draft)
    writers.write_outreach_draft(campaign_id, account_id, draft_payload)

    research_report = readers.read_optional_json(paths.research_dir(campaign_id) / f"{account_id}.json") or {}
    signal_report = readers.read_optional_json(paths.signals_dir(campaign_id) / f"{account_id}.json") or {}
    quality_review = review_outreach_quality(draft_payload, research_report, signal_report)
    writers.write_quality_review(campaign_id, account_id, quality_review)
    updated_draft = update_outreach_quality_status(db, account_id, quality_review["quality_status"]) or draft

    event_service.record_event(
        db,
        campaign_id,
        "draft_updated",
        "Outreach draft updated",
        {
            "account_id": account.id,
            "company_name": account.company_name,
            "fields_updated": sorted(payload.keys()),
        },
    )
    event_service.record_event(
        db,
        campaign_id,
        "quality_review_updated",
        "Quality review updated after draft edit",
        {
            "account_id": account.id,
            "company_name": account.company_name,
            "quality_status": quality_review["quality_status"],
        },
    )

    return updated_draft


def _validate_outreach_draft_update(payload: dict[str, str | None]) -> None:
    if not payload:
        raise ValueError("At least one draft field must be provided.")

    if "subject" in payload:
        subject = (payload.get("subject") or "").strip()
        if not subject:
            raise ValueError("Subject cannot be empty.")
        if len(subject) > 200:
            raise ValueError("Subject must be 200 characters or fewer.")
        payload["subject"] = subject

    if "body" in payload:
        body = (payload.get("body") or "").strip()
        if not body:
            raise ValueError("Body cannot be empty.")
        if len(body) > 2000:
            raise ValueError("Body must be 2000 characters or fewer.")
        payload["body"] = body

    if "sales_angle" in payload and payload["sales_angle"] is not None:
        payload["sales_angle"] = payload["sales_angle"].strip()

    if "personalization_source" in payload and payload["personalization_source"] is not None:
        payload["personalization_source"] = payload["personalization_source"].strip()

    if "personalization_source_url" in payload and payload["personalization_source_url"] is not None:
        payload["personalization_source_url"] = payload["personalization_source_url"].strip()


def _build_outreach_workspace_payload(
    campaign_id: str,
    account_id: str,
    company_name: str,
    domain: str,
    draft: OutreachDraft,
) -> dict:
    existing = readers.read_optional_json(paths.outreach_dir(campaign_id) / f"{account_id}.json") or {}
    existing.update(
        {
            "company_name": existing.get("company_name") or company_name,
            "domain": existing.get("domain") or domain,
            "subject": draft.subject,
            "body": draft.body,
            "personalization_source": draft.personalization_source,
            "personalization_source_url": draft.personalization_source_url,
            "sales_angle": draft.sales_angle,
            "risk_notes": draft.risk_notes or [],
            "quality_status": draft.quality_status,
            "updated_at": draft.updated_at.isoformat() if draft.updated_at else None,
        }
    )
    return existing
