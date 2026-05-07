from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Account, OutreachDraft, ResearchReport, ScoreReport, SignalReport
from app.schemas.account import AccountResponse
from app.schemas.outreach import QualityReviewResponse
from app.services import account_service, campaign_service
from app.tools.export_tools import sort_accounts_by_overall_score
from app.utils.ids import new_id
from app.utils.timestamps import utc_now
from app.workspace import readers, paths


def upsert_research_report(db: Session, account_id: str, data: dict, workspace_file: str) -> ResearchReport:
    report = db.scalars(select(ResearchReport).where(ResearchReport.account_id == account_id)).first()
    now = utc_now()
    if report is None:
        report = ResearchReport(id=new_id("research"), account_id=account_id, created_at=now, updated_at=now)
        db.add(report)
    report.company_summary = data["company_summary"]
    report.business_model = data["business_model"]
    report.fit_claims = data["fit_claims"]
    report.evidence = data["evidence"]
    report.risks = data["risks"]
    report.confidence = data["confidence"]
    report.workspace_file = workspace_file
    report.updated_at = now
    db.commit()
    db.refresh(report)
    return report


def upsert_signal_report(db: Session, account_id: str, data: dict, workspace_file: str) -> SignalReport:
    report = db.scalars(select(SignalReport).where(SignalReport.account_id == account_id)).first()
    now = utc_now()
    if report is None:
        report = SignalReport(id=new_id("signal"), account_id=account_id, created_at=now, updated_at=now)
        db.add(report)
    report.signals = data["signals"]
    report.timing_score = data["timing_score"]
    report.why_now = data["why_now"]
    report.confidence = data["confidence"]
    report.workspace_file = workspace_file
    report.updated_at = now
    db.commit()
    db.refresh(report)
    return report


def upsert_score_report(db: Session, account_id: str, data: dict, workspace_file: str) -> ScoreReport:
    report = db.scalars(select(ScoreReport).where(ScoreReport.account_id == account_id)).first()
    now = utc_now()
    if report is None:
        report = ScoreReport(id=new_id("score"), account_id=account_id, created_at=now, updated_at=now)
        db.add(report)
    report.fit_score = data["fit_score"]
    report.timing_score = data["timing_score"]
    report.confidence_score = data["confidence_score"]
    report.persona_score = data["persona_score"]
    report.overall_score = data["overall_score"]
    report.score_explanation = data["score_explanation"]
    report.score_breakdown = data["score_breakdown"]
    report.recommended_persona = data["recommended_persona"]
    report.sales_angle = data["sales_angle"]
    report.workspace_file = workspace_file
    report.updated_at = now
    db.commit()
    db.refresh(report)
    return report


def upsert_outreach_draft(db: Session, account_id: str, data: dict, workspace_file: str) -> OutreachDraft:
    draft = db.scalars(select(OutreachDraft).where(OutreachDraft.account_id == account_id)).first()
    now = utc_now()
    if draft is None:
        draft = OutreachDraft(id=new_id("draft"), account_id=account_id, created_at=now, updated_at=now)
        db.add(draft)
    draft.subject = data["subject"]
    draft.body = data["body"]
    draft.personalization_source = data["personalization_source"]
    draft.personalization_source_url = data.get("personalization_source_url")
    draft.sales_angle = data["sales_angle"]
    draft.risk_notes = data["risk_notes"]
    draft.workspace_file = workspace_file
    draft.updated_at = now
    db.commit()
    db.refresh(draft)
    return draft


def update_outreach_quality_status(db: Session, account_id: str, quality_status: str) -> OutreachDraft | None:
    draft = db.scalars(select(OutreachDraft).where(OutreachDraft.account_id == account_id)).first()
    if draft is None:
        return None
    draft.quality_status = quality_status
    draft.updated_at = utc_now()
    db.commit()
    db.refresh(draft)
    return draft


def get_campaign_results(db: Session, campaign_id: str) -> dict:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise ValueError("Campaign not found")

    statement = (
        select(Account, ScoreReport, OutreachDraft)
        .outerjoin(ScoreReport, ScoreReport.account_id == Account.id)
        .outerjoin(OutreachDraft, OutreachDraft.account_id == Account.id)
        .where(Account.campaign_id == campaign_id)
    )

    accounts: list[dict] = []
    for account, score, draft in db.execute(statement).all():
        accounts.append(
            {
                "account_id": account.id,
                "company_name": account.company_name,
                "domain": account.domain,
                "overall_score": _as_int(score.overall_score if score else None),
                "fit_score": _as_int(score.fit_score if score else None),
                "timing_score": _as_int(score.timing_score if score else None),
                "confidence_score": _as_int(score.confidence_score if score else None),
                "persona_score": _as_int(score.persona_score if score else None),
                "recommended_persona": score.recommended_persona if score else None,
                "sales_angle": score.sales_angle if score else None,
                "review_status": account.review_status,
                "research_status": account.research_status,
                "draft_quality_status": draft.quality_status if draft else None,
            }
        )

    return {
        "campaign_id": campaign.id,
        "status": campaign.status,
        "accounts": sort_accounts_by_overall_score(accounts),
    }


def get_account_detail(db: Session, campaign_id: str, account_id: str) -> dict | None:
    account = account_service.get_account(db, campaign_id, account_id)
    if account is None:
        return None

    quality_review = readers.read_optional_json(paths.review_dir(campaign_id) / f"{account_id}.json")
    detail = {
        "account": AccountResponse.model_validate(account).model_dump(mode="json"),
        "research_report": readers.read_optional_json(paths.research_dir(campaign_id) / f"{account_id}.json"),
        "signal_report": readers.read_optional_json(paths.signals_dir(campaign_id) / f"{account_id}.json"),
        "score_report": readers.read_optional_json(paths.scores_dir(campaign_id) / f"{account_id}.json"),
        "outreach_draft": readers.read_optional_json(paths.outreach_dir(campaign_id) / f"{account_id}.json"),
        "quality_review": (
            QualityReviewResponse.model_validate(quality_review).model_dump(mode="json")
            if quality_review is not None
            else None
        ),
    }
    return detail


def _as_int(value: float | None) -> int | None:
    return None if value is None else int(round(value))
