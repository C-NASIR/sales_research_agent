from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.errors import not_found
from app.db.models import Account, Campaign
from app.services import account_service, campaign_service


def get_campaign_or_404(db: Session, campaign_id: str) -> Campaign:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise not_found("Campaign not found")
    return campaign


def get_account_or_404(db: Session, campaign_id: str, account_id: str) -> Account:
    account = account_service.get_account(db, campaign_id, account_id)
    if account is None:
        raise not_found("Account not found")
    return account
