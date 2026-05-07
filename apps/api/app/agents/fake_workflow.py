from __future__ import annotations

from app.agents.schemas import (
    ICPProfile,
    OutreachDraftData,
    QualityReviewData,
    ResearchReportData,
    RiskItem,
    ScoreReportData,
    SignalItem,
    SignalReportData,
    TodoItem,
)
from app.tools.fake_research_tools import build_company_profile
from app.tools.outreach_tools import build_outreach_draft
from app.tools.quality_review_tools import review_outreach_quality
from app.tools.scoring_tools import build_score_report


def build_fake_todos() -> list[dict]:
    todos = [
        TodoItem(id="todo_icp", title="Define ICP and rubric", status="pending"),
        TodoItem(id="todo_research", title="Generate simulated research reports", status="pending"),
        TodoItem(id="todo_signals", title="Generate simulated timing signals", status="pending"),
        TodoItem(id="todo_scoring", title="Score accounts deterministically", status="pending"),
        TodoItem(id="todo_outreach", title="Draft outreach and review quality", status="pending"),
    ]
    return [todo.model_dump(mode="json") for todo in todos]


def fake_icp_strategist(brief: dict) -> dict:
    personas = [item.strip() for item in brief.get("target_persona", "").split(",") if item.strip()]
    icp = ICPProfile(
        target_company_criteria=[
            brief.get("ideal_customer_profile", "B2B teams with meaningful engineering workflow needs."),
            "Accounts that can plausibly support technical decision-makers.",
        ],
        target_personas=personas or ["VP Engineering"],
        positive_signals=[
            "Developer or technical product surface",
            "Need for consistent engineering workflow quality",
            "Multi-team coordination or platform complexity",
        ],
        negative_signals=[
            "Very small team with little process overhead",
            "No clear software or workflow ownership",
        ],
        scoring_rubric={
            "fit": "How closely the company appears to match the ICP.",
            "timing": "Simulated urgency based on the fake signal pass.",
            "confidence": "How believable the Phase 3 simulated evidence looks.",
            "persona": "How clearly the campaign persona maps to the account.",
        },
    )
    return icp.model_dump(mode="json")


def fake_account_researcher(account: dict, icp: dict) -> dict:
    company_name = account["company_name"]
    domain = account["domain"]
    profile = build_company_profile(company_name, domain)
    homepage = f"https://{domain}"
    report = ResearchReportData(
        company_name=company_name,
        domain=domain,
        company_summary=(
            f"{company_name} is treated as a {profile['summary']} for the Phase 3 simulated workflow. "
            "Real web research is not implemented until Phase 4."
        ),
        business_model=profile["business_model"],
        fit_claims=[
            {
                "claim": f"{company_name} appears aligned with the target campaign profile.",
                "evidence": (
                    f"The uploaded domain {domain} and the simulated category imply relevance to "
                    f"{icp['target_personas'][0] if icp.get('target_personas') else 'technical buyers'}."
                ),
                "source_url": homepage,
                "source_title": company_name,
                "confidence": "medium",
                "evidence_type": "homepage",
            }
        ],
        evidence=[
            {
                "claim": "Public company website exists",
                "evidence": f"The uploaded domain for this account is {domain}. Real verification is deferred to Phase 4.",
                "source_url": homepage,
                "source_title": company_name,
                "confidence": "medium",
                "evidence_type": "homepage",
            }
        ],
        risks=[
            RiskItem(
                risk="Evidence is simulated in Phase 3",
                reason="Real web research and source collection are not implemented yet.",
                confidence="high",
            )
        ],
        confidence=65 if company_name.lower() not in {"sentry", "posthog", "linear", "retool", "vercel"} else 74,
        sources=[{"url": homepage, "title": company_name, "source": "phase3_fake"}],
    )
    return report.model_dump(mode="json")


def fake_signal_detector(account: dict, research_report: dict, icp: dict) -> dict:
    profile = build_company_profile(account["company_name"], account["domain"])
    domain_url = f"https://{account['domain']}"
    signal = SignalItem(
        type="simulated_timing_signal",
        description=profile["timing_signal"],
        why_it_matters=(
            f"This simulated signal suggests relevance to {icp['target_personas'][0] if icp.get('target_personas') else 'technical leaders'}."
        ),
        source_url=domain_url,
        confidence="medium",
    )
    report = SignalReportData(
        company_name=account["company_name"],
        domain=account["domain"],
        signals=[signal],
        timing_score=68 if "developer" in research_report["company_summary"].lower() else 58,
        why_now=(
            "Timing analysis is simulated in Phase 3 and should be treated as a placeholder until real research is added."
        ),
        confidence=60,
        sources=[{"url": domain_url, "title": account["company_name"], "source": "phase3_fake"}],
    )
    return report.model_dump(mode="json")


def fake_scoring_analyst(account: dict, brief: dict, research_report: dict, signal_report: dict, icp: dict) -> dict:
    score_data = build_score_report(account, brief, icp, research_report, signal_report)
    report = ScoreReportData(**score_data)
    return report.model_dump(mode="json")


def fake_outreach_writer(
    brief: dict,
    account: dict,
    research_report: dict,
    signal_report: dict,
    score_report: dict,
) -> dict:
    draft_payload = build_outreach_draft(account, brief, research_report, signal_report, score_report)
    risk_notes = list(draft_payload["risk_notes"])
    if "simulated" in (research_report.get("company_summary") or "").lower():
        risk_notes.append(f"Campaign tone requested: {brief['tone']}.")
    draft = OutreachDraftData(
        company_name=account["company_name"],
        domain=account["domain"],
        subject=draft_payload["subject"],
        body=draft_payload["body"],
        personalization_source=draft_payload["personalization_source"],
        personalization_source_url=draft_payload["personalization_source_url"],
        sales_angle=draft_payload["sales_angle"],
        risk_notes=risk_notes,
    )
    return draft.model_dump(mode="json")


def fake_compliance_reviewer(outreach_draft: dict, research_report: dict, signal_report: dict) -> dict:
    review = QualityReviewData(**review_outreach_quality(outreach_draft, research_report, signal_report))
    return review.model_dump(mode="json")
