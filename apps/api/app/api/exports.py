from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_campaign_or_404
from app.api.errors import not_found
from app.db.session import get_db
from app.schemas.export import (
    ExportCreateRequest,
    ExportCreateResponse,
    ExportFileResponse,
    ExportListResponse,
)
from app.services import export_service
from app.workspace import paths

router = APIRouter(tags=["exports"])


@router.post("/campaigns/{campaign_id}/exports", response_model=ExportCreateResponse)
def create_exports(
    campaign_id: str,
    input: ExportCreateRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> ExportCreateResponse:
    get_campaign_or_404(db, campaign_id)

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
    get_campaign_or_404(db, campaign_id)

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
    get_campaign_or_404(db, campaign_id)

    export_file = export_service.get_campaign_export(db, campaign_id, export_id)
    if export_file is None:
        raise not_found("Export not found")

    path = _resolve_export_path(campaign_id, export_file.file_path)
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


def _resolve_export_path(campaign_id: str, file_path: str) -> Path:
    exports_root = paths.exports_dir(campaign_id).resolve()
    resolved = Path(file_path).expanduser().resolve()

    try:
        resolved.relative_to(exports_root)
    except ValueError as error:
        raise not_found("Export file not found") from error

    if not resolved.is_file():
        raise not_found("Export file not found")

    return resolved
