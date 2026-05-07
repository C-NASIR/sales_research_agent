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
from app.tools.scoring_tools import (
    calculate_confidence_score,
    calculate_fit_score,
    calculate_overall_score,
    calculate_persona_score,
)


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


def fake_scoring_analyst(account: dict, research_report: dict, signal_report: dict, icp: dict) -> dict:
    profile = build_company_profile(account["company_name"], account["domain"])
    fit_score = calculate_fit_score(research_report.get("fit_claims"))
    timing_score = int(signal_report["timing_score"])
    confidence_score = calculate_confidence_score(research_report.get("evidence"))
    persona_score = calculate_persona_score(icp.get("target_personas", []), profile["recommended_persona"])
    overall_score = calculate_overall_score(fit_score, timing_score, confidence_score, persona_score)
    report = ScoreReportData(
        company_name=account["company_name"],
        domain=account["domain"],
        fit_score=fit_score,
        timing_score=timing_score,
        confidence_score=confidence_score,
        persona_score=persona_score,
        overall_score=overall_score,
        score_explanation=(
            "This Phase 3 score is deterministic and based on simulated fit, timing, confidence, and persona alignment."
        ),
        score_breakdown={
            "fit_weight": 0.45,
            "timing_weight": 0.25,
            "confidence_weight": 0.20,
            "persona_weight": 0.10,
        },
        recommended_persona=profile["recommended_persona"],
        sales_angle=profile["sales_angle"],
    )
    return report.model_dump(mode="json")


def fake_outreach_writer(
    brief: dict,
    account: dict,
    research_report: dict,
    signal_report: dict,
    score_report: dict,
) -> dict:
    subject = f"{score_report['sales_angle']} at {account['company_name']}"
    evidence_items = research_report.get("evidence") or []
    simulated = "simulated" in (research_report.get("company_summary", "") or "").lower()
    if simulated:
        body = (
            f"Hi there,\n\n"
            f"I’m reviewing teams that may care about {score_report['sales_angle'].lower()}. "
            f"{account['company_name']} looks relevant because the Phase 3 simulated research suggests a technical product surface. "
            f"We help engineering teams reduce review bottlenecks and keep code quality consistent.\n\n"
            f"Worth a quick comparison?\n"
        )
        personalization_source = (
            f"Phase 3 simulated research based on uploaded company name, domain, and campaign tone '{brief['tone']}'."
        )
    elif evidence_items:
        anchor = evidence_items[0]
        body = (
            f"Hi there,\n\n"
            f"I came across {account['company_name']} while researching teams in this market. "
            f"One public source suggests: {anchor['evidence'][:120]}. "
            f"We help engineering teams reduce review bottlenecks and keep code quality consistent.\n\n"
            f"Worth a quick comparison?\n"
        )
        personalization_source = f"{anchor.get('source_title') or account['company_name']} - {anchor['source_url']}"
    else:
        body = (
            f"Hi there,\n\n"
            f"I came across {account['company_name']} while researching teams in this market. "
            f"We help engineering teams reduce review bottlenecks and keep code quality consistent.\n\n"
            f"Worth a quick comparison?\n"
        )
        personalization_source = ""
    draft = OutreachDraftData(
        company_name=account["company_name"],
        domain=account["domain"],
        subject=subject,
        body=body[:700],
        personalization_source=personalization_source,
        sales_angle=score_report["sales_angle"],
        risk_notes=[
            (
                "Draft is based on simulated research, not verified web evidence."
                if simulated
                else "Draft quality depends on the strength of the cited public evidence."
            ),
            f"Timing explanation: {signal_report['why_now']}",
        ],
    )
    return draft.model_dump(mode="json")


def fake_compliance_reviewer(outreach_draft: dict, research_report: dict, signal_report: dict) -> dict:
    body_text = (outreach_draft.get("body") or "").lower()
    banned_phrases = [
        "following up",
        "as discussed",
        "our conversation",
        "you asked",
        "circling back",
    ]
    issues: list[str] = []
    if not outreach_draft.get("subject"):
        issues.append("Subject is empty.")
    if not outreach_draft.get("body"):
        issues.append("Body is empty.")
    if not outreach_draft.get("personalization_source"):
        issues.append("Personalization source is empty.")
    if any(phrase in body_text for phrase in banned_phrases):
        issues.append("Body contains unsupported familiarity language.")
    evidence_items = research_report.get("evidence") or []
    if not evidence_items:
        issues.append("Research evidence is empty.")
    if any(not item.get("source_url") for item in evidence_items):
        issues.append("At least one evidence item is missing a source URL.")
    if research_report.get("confidence", 0) < 50:
        issues.append("Research confidence is low.")
    unsupported_pain_terms = ["struggling", "pain", "suffering", "blocked by"]
    if any(term in body_text for term in unsupported_pain_terms):
        evidence_text = " ".join(item.get("evidence", "").lower() for item in evidence_items)
        if not any(term in evidence_text for term in unsupported_pain_terms):
            issues.append("Draft claims pain that is not directly supported by evidence.")

    quality_status = "approved_by_reviewer" if not issues else "flagged"
    review = QualityReviewData(
        company_name=outreach_draft["company_name"],
        domain=outreach_draft["domain"],
        quality_status=quality_status,
        issues=issues,
        blocked_reasons=[],
        recommended_edits=(
            []
            if not issues
            else [
                "Remove unsupported familiarity phrases.",
                "Keep personalization anchored to the Phase 3 simulated research summary.",
            ]
        ),
    )
    return review.model_dump(mode="json")
