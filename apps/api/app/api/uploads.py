from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.upload import (
    UploadAccountPreview,
    UploadDuplicateRow,
    UploadReportResponse,
)
from app.services import account_service, campaign_service, csv_service, event_service, workspace_service

router = APIRouter(tags=["uploads"])


@router.post("/campaigns/{campaign_id}/upload", response_model=UploadReportResponse)
async def upload_campaign_accounts(
    campaign_id: str,
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> UploadReportResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    if file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is required")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    event_service.record_event(
        db,
        campaign_id=campaign_id,
        type="csv_upload_started",
        message="CSV upload started",
        payload={"filename": file.filename},
    )

    try:
        parsed = csv_service.parse_accounts_csv(file_bytes)
    except csv_service.CSVValidationError as exc:
        event_service.record_event(
            db,
            campaign_id=campaign_id,
            type="csv_upload_failed",
            message="CSV upload failed",
            payload={"error": str(exc)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    existing_domains = account_service.get_existing_domains_for_campaign(db, campaign_id)
    accounts_to_create: list[dict[str, str]] = []
    duplicate_rows = list(parsed.duplicate_rows)

    for candidate in parsed.valid_accounts:
        if candidate.domain in existing_domains:
            duplicate_rows.append(
                UploadDuplicateRow(
                    row_number=candidate.row_number,
                    company_name=candidate.company_name,
                    domain=candidate.domain,
                    duplicate_of_domain=candidate.domain,
                )
            )
            continue

        accounts_to_create.append(
            {
                "company_name": candidate.company_name,
                "domain": candidate.domain,
            }
        )
        existing_domains.add(candidate.domain)

    workspace_service.ensure_campaign_workspace(campaign)
    workspace_service.write_uploaded_csv(campaign, file_bytes)

    created_accounts = account_service.create_accounts_for_campaign(db, campaign_id, accounts_to_create)
    persisted_accounts = account_service.list_accounts_for_campaign(db, campaign_id)
    workspace_service.write_normalized_accounts(
        campaign,
        [
            {
                "company_name": account.company_name,
                "domain": account.domain,
            }
            for account in persisted_accounts
        ],
    )

    event_service.record_event(
        db,
        campaign_id=campaign_id,
        type="accounts_created",
        message="Accounts created",
        payload={"created_accounts": len(created_accounts)},
    )

    if created_accounts:
        campaign = campaign_service.update_campaign_status(db, campaign_id, "ready") or campaign
        event_service.record_event(
            db,
            campaign_id=campaign_id,
            type="campaign_ready",
            message="Campaign is ready for the next phase",
            payload={"status": campaign.status},
        )

    report = UploadReportResponse(
        campaign_id=campaign_id,
        valid_rows=len(accounts_to_create),
        invalid_rows=len(parsed.invalid_rows),
        duplicate_rows=len(duplicate_rows),
        created_accounts=len(created_accounts),
        accounts=[
            UploadAccountPreview(
                id=account.id,
                company_name=account.company_name,
                domain=account.domain,
            )
            for account in created_accounts
        ],
        invalid=parsed.invalid_rows,
        duplicates=duplicate_rows,
    )

    workspace_service.write_upload_report(campaign, report.model_dump(mode="json"))
    event_service.record_event(
        db,
        campaign_id=campaign_id,
        type="csv_upload_completed",
        message="CSV upload completed",
        payload={
            "valid_rows": report.valid_rows,
            "invalid_rows": report.invalid_rows,
            "duplicate_rows": report.duplicate_rows,
            "created_accounts": report.created_accounts,
        },
    )
    return report
