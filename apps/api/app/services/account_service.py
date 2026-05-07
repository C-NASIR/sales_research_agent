from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Account


def list_accounts_for_campaign(db: Session, campaign_id: str) -> list[Account]:
    statement = (
        select(Account)
        .where(Account.campaign_id == campaign_id)
        .order_by(Account.created_at.asc())
    )
    return list(db.scalars(statement).all())


def get_account(db: Session, campaign_id: str, account_id: str) -> Account | None:
    statement = select(Account).where(
        Account.campaign_id == campaign_id,
        Account.id == account_id,
    )
    return db.scalars(statement).first()
