from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Campaign
from app.schemas.campaign import CampaignCreate
from app.services import workspace_service
from app.utils.ids import new_id
from app.utils.timestamps import utc_now


def create_campaign(db: Session, data: CampaignCreate) -> Campaign:
    campaign_id = new_id("campaign")
    created_at = utc_now()
    campaign = Campaign(
        id=campaign_id,
        name=data.name,
        product_description=data.product_description,
        ideal_customer_profile=data.ideal_customer_profile,
        pain_statement=data.pain_statement,
        target_persona=data.target_persona,
        tone=data.tone,
        max_accounts=data.max_accounts,
        status="draft",
        workspace_path=str(settings.data_dir / "campaigns" / campaign_id),
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    workspace_service.ensure_campaign_workspace(campaign)
    workspace_service.write_campaign_brief(campaign)
    return campaign


def get_campaign(db: Session, campaign_id: str) -> Campaign | None:
    return db.get(Campaign, campaign_id)


def list_campaigns(db: Session) -> list[Campaign]:
    statement = select(Campaign).order_by(Campaign.created_at.desc())
    return list(db.scalars(statement).all())


def update_campaign_status(db: Session, campaign_id: str, status: str) -> Campaign | None:
    campaign = get_campaign(db, campaign_id)
    if campaign is None:
        return None

    campaign.status = status
    campaign.updated_at = utc_now()
    db.commit()
    db.refresh(campaign)
    workspace_service.write_campaign_brief(campaign)
    return campaign
