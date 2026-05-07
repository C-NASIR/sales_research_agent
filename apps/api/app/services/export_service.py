from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ExportFile
from app.schemas.account import AccountResponse
from app.schemas.review import REVIEW_STATUSES
from app.services import account_service, campaign_service, event_service, result_service
from app.tools.export_tools import (
    build_archive_json,
    build_campaign_report_markdown,
    build_prospects_csv,
)
from app.utils.ids import new_id
from app.utils.timestamps import utc_now
from app.workspace import paths

EXPORT_DEFINITIONS = (
    ("prospects_csv", "prospects.csv"),
    ("campaign_report_md", "campaign_report.md"),
    ("archive_json", "archive.json"),
)


def validate_export_review_statuses(include_review_statuses: list[str]) -> list[str]:
    if not include_review_statuses:
        raise ValueError("At least one review status is required for export.")

    normalized = []
    for item in include_review_statuses:
        status = item.strip()
        if status not in REVIEW_STATUSES:
            raise ValueError("Invalid review status in export request.")
        if status not in normalized:
            normalized.append(status)
    return normalized


def create_campaign_exports(
    db: Session,
    campaign_id: str,
    include_review_statuses: list[str],
) -> list[ExportFile]:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise ValueError("Campaign not found")

    statuses = validate_export_review_statuses(include_review_statuses)
    selected_accounts = [
        account
        for account in account_service.list_accounts_for_campaign(db, campaign_id)
        if account.review_status in statuses
    ]
    if not selected_accounts:
        event_service.record_event(
            db,
            campaign_id,
            "export_failed",
            "Export failed because no accounts matched the requested review statuses",
            {"include_review_statuses": statuses},
        )
        raise ValueError("No accounts are available for export.")

    rows = [
        result_service.get_account_detail(db, campaign_id, account.id)
        for account in selected_accounts
    ]
    rows = [row for row in rows if row is not None]

    export_meta = {
        "id": campaign.id,
        "name": campaign.name,
        "product_description": campaign.product_description,
        "ideal_customer_profile": campaign.ideal_customer_profile,
        "pain_statement": campaign.pain_statement,
        "target_persona": campaign.target_persona,
        "tone": campaign.tone,
        "status": campaign.status,
        "exported_at": utc_now().isoformat(),
        "include_review_statuses": statuses,
    }

    exports_dir = paths.exports_dir(campaign_id)
    build_prospects_csv(rows, exports_dir / "prospects.csv")
    build_campaign_report_markdown(export_meta, rows, exports_dir / "campaign_report.md")
    build_archive_json(export_meta, rows, exports_dir / "archive.json")

    exports = [_upsert_export_file(db, campaign_id, export_type, exports_dir / filename) for export_type, filename in EXPORT_DEFINITIONS]

    event_service.record_event(
        db,
        campaign_id,
        "exports_created",
        "Campaign exports created",
        {
            "export_count": len(exports),
            "include_review_statuses": statuses,
        },
    )
    return exports


def list_campaign_exports(db: Session, campaign_id: str) -> list[ExportFile]:
    statement = (
        select(ExportFile)
        .where(ExportFile.campaign_id == campaign_id)
        .order_by(ExportFile.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_campaign_export(db: Session, campaign_id: str, export_id: str) -> ExportFile | None:
    statement = select(ExportFile).where(
        ExportFile.campaign_id == campaign_id,
        ExportFile.id == export_id,
    )
    return db.scalars(statement).first()


def _upsert_export_file(
    db: Session,
    campaign_id: str,
    export_type: str,
    file_path: Path,
) -> ExportFile:
    statement = select(ExportFile).where(
        ExportFile.campaign_id == campaign_id,
        ExportFile.export_type == export_type,
    )
    export_file = db.scalars(statement).first()
    if export_file is None:
        export_file = ExportFile(
            id=new_id("export"),
            campaign_id=campaign_id,
            export_type=export_type,
            file_path=str(file_path),
            created_at=utc_now(),
        )
        db.add(export_file)
    else:
        export_file.file_path = str(file_path)
        export_file.created_at = utc_now()

    db.commit()
    db.refresh(export_file)
    return export_file
