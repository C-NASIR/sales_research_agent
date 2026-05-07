from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.export import (
    ExportCreateRequest,
    ExportCreateResponse,
    ExportFileResponse,
    ExportListResponse,
)
from app.services import campaign_service, export_service

router = APIRouter(tags=["exports"])


@router.post("/campaigns/{campaign_id}/exports", response_model=ExportCreateResponse)
def create_exports(
    campaign_id: str,
    input: ExportCreateRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> ExportCreateResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    try:
        exports = export_service.create_campaign_exports(
            db,
            campaign_id,
            (input.include_review_statuses if input is not None else ["approved"]),
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    return ExportCreateResponse(
        campaign_id=campaign_id,
        exports=[_to_export_response(item) for item in exports],
    )


@router.get("/campaigns/{campaign_id}/exports", response_model=ExportListResponse)
def list_exports(campaign_id: str, db: Session = Depends(get_db)) -> ExportListResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    exports = export_service.list_campaign_exports(db, campaign_id)
    return ExportListResponse(
        campaign_id=campaign_id,
        exports=[_to_export_response(item) for item in exports],
    )


@router.get("/campaigns/{campaign_id}/exports/{export_id}/download")
def download_export(
    campaign_id: str,
    export_id: str,
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    export_file = export_service.get_campaign_export(db, campaign_id, export_id)
    if export_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")

    path = Path(export_file.file_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export file not found")

    filename, media_type = _download_meta(export_file.export_type)
    return FileResponse(path, filename=filename, media_type=media_type)


def _to_export_response(export_file) -> ExportFileResponse:
    return ExportFileResponse(
        id=export_file.id,
        campaign_id=export_file.campaign_id,
        export_type=export_file.export_type,
        file_path=export_file.file_path,
        download_url=f"/campaigns/{export_file.campaign_id}/exports/{export_file.id}/download",
        created_at=export_file.created_at,
    )


def _download_meta(export_type: str) -> tuple[str, str]:
    if export_type == "prospects_csv":
        return ("prospects.csv", "text/csv")
    if export_type == "campaign_report_md":
        return ("campaign_report.md", "text/markdown")
    return ("archive.json", "application/json")
