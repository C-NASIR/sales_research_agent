from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Account
from app.utils.ids import new_id
from app.utils.timestamps import utc_now


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


def get_existing_domains_for_campaign(db: Session, campaign_id: str) -> set[str]:
    statement = select(Account.domain).where(Account.campaign_id == campaign_id)
    return set(db.scalars(statement).all())


def create_accounts_for_campaign(
    db: Session,
    campaign_id: str,
    accounts: Sequence[dict[str, str]],
) -> list[Account]:
    existing_domains = get_existing_domains_for_campaign(db, campaign_id)
    created_accounts: list[Account] = []

    for account_data in accounts:
        domain = account_data["domain"]
        if domain in existing_domains:
            continue

        account = Account(
            id=new_id("account"),
            campaign_id=campaign_id,
            company_name=account_data["company_name"],
            domain=domain,
            research_status="pending",
            review_status="unreviewed",
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(account)
        created_accounts.append(account)
        existing_domains.add(domain)

    db.commit()
    for account in created_accounts:
        db.refresh(account)
    return created_accounts
