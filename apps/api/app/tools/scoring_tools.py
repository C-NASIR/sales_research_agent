from __future__ import annotations

from app.tools.outreach_tools import generate_sales_angle
from app.tools.persona_tools import recommend_persona

RELEVANT_TERM_KEYWORDS = [
    "product",
    "engineering",
    "growth",
    "sales",
    "security",
    "compliance",
    "data",
    "developer",
    "developers",
    "platform",
    "workflow",
    "analytics",
    "review",
]

HIGH_CONFIDENCE_SIGNAL_TYPES = {
    "hiring_signal",
    "product_focus_signal",
    "funding_signal",
    "compliance_signal",
    "growth_signal",
}


def clamp_score(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


def calculate_overall_score(
    fit_score: int,
    timing_score: int,
    confidence_score: int,
    persona_score: int,
) -> int:
    overall = (
        clamp_score(fit_score) * 0.45
        + clamp_score(timing_score) * 0.25
        + clamp_score(confidence_score) * 0.20
        + clamp_score(persona_score) * 0.10
    )
    return clamp_score(round(overall))


def calculate_fit_score(research_report: dict, campaign_brief: dict, icp: dict) -> tuple[int, dict]:
    score = 40
    adjustments: list[str] = []
    fit_claims = research_report.get("fit_claims") or []
    evidence_text = _combined_text(
        research_report.get("company_summary"),
        research_report.get("business_model"),
        *[item.get("evidence") for item in fit_claims],
        *[item.get("evidence") for item in research_report.get("evidence") or []],
    )
    icp_text = _combined_text(
        campaign_brief.get("ideal_customer_profile"),
        campaign_brief.get("product_description"),
        campaign_brief.get("pain_statement"),
        *(icp.get("target_company_criteria") or []),
        *(icp.get("positive_signals") or []),
    )

    for claim in fit_claims:
        confidence = claim.get("confidence")
        if confidence == "high":
            score += 15
            adjustments.append("High-confidence fit claim")
        elif confidence == "medium":
            score += 10
            adjustments.append("Medium-confidence fit claim")

    if _business_model_matches_icp(research_report.get("business_model"), icp_text):
        score += 10
        adjustments.append("Business model appears aligned with the ICP")

    if _company_category_relevant(evidence_text, campaign_brief, icp_text):
        score += 10
        adjustments.append("Company category appears relevant to the campaign")

    if any(keyword in evidence_text for keyword in RELEVANT_TERM_KEYWORDS):
        score += 5
        adjustments.append("Evidence includes campaign-relevant terms")

    risks = research_report.get("risks") or []
    if _has_risk(risks, "insufficient evidence"):
        score -= 20
        adjustments.append("Insufficient evidence risk lowered fit")

    if _has_risk(risks, "outside the icp") or "outside the icp" in evidence_text:
        score -= 15
        adjustments.append("Research suggests the company may be outside the ICP")

    if _business_model_unclear(research_report.get("business_model")):
        score -= 10
        adjustments.append("Business model is unclear")

    score = clamp_score(score)
    return score, {
        "base": 40,
        "adjustments": adjustments,
        "fit_claim_count": len(fit_claims),
        "risk_count": len(risks),
        "business_model": research_report.get("business_model"),
        "score": score,
    }


def calculate_timing_score(signal_report: dict) -> tuple[int, dict]:
    base = clamp_score(signal_report.get("timing_score", 0) or 0)
    score = base
    adjustments: list[str] = []
    signals = signal_report.get("signals") or []
    medium_or_high = [item for item in signals if item.get("confidence") in {"medium", "high"}]
    high_priority = [
        item
        for item in signals
        if item.get("confidence") == "high" and item.get("type") in HIGH_CONFIDENCE_SIGNAL_TYPES
    ]

    if len(medium_or_high) >= 2:
        score += 10
        adjustments.append("Multiple medium or high confidence timing signals")

    if high_priority:
        score += 10
        adjustments.append("High-confidence timing signal present")

    if not signals:
        score -= 20
        adjustments.append("No timing signals found")
    elif all(item.get("confidence") == "low" for item in signals):
        score -= 10
        adjustments.append("All timing signals are low confidence")

    score = clamp_score(score)
    return score, {
        "base": base,
        "adjustments": adjustments,
        "signal_count": len(signals),
        "medium_or_high_count": len(medium_or_high),
        "score": score,
    }


def calculate_confidence_score(research_report: dict, signal_report: dict) -> tuple[int, dict]:
    score = 30
    adjustments: list[str] = []
    evidence_items = research_report.get("evidence") or []
    signals = signal_report.get("signals") or []
    evidence_urls = {item.get("source_url") for item in evidence_items if item.get("source_url")}

    with_source = sum(1 for item in evidence_items if item.get("source_url"))
    score += with_source * 10
    if with_source:
        adjustments.append(f"{with_source} evidence items include source URLs")

    if any(item.get("confidence") == "high" for item in evidence_items):
        score += 10
        adjustments.append("At least one high-confidence evidence item exists")

    if len(evidence_urls) >= 2:
        score += 10
        adjustments.append("Research uses at least two distinct source URLs")

    if any(item.get("source_url") for item in signals):
        score += 10
        adjustments.append("Timing signals include source URLs")

    if not evidence_items:
        score -= 20
        adjustments.append("No research evidence exists")

    if evidence_items and any(not item.get("source_url") for item in evidence_items):
        score -= 15
        adjustments.append("Some evidence items are missing source URLs")

    risks = research_report.get("risks") or []
    if _has_risk(risks, "insufficient evidence"):
        score -= 10
        adjustments.append("Research report flags insufficient evidence")

    if _mostly_inference(research_report):
        score -= 10
        adjustments.append("Research appears inference-heavy")

    score = clamp_score(score)
    return score, {
        "base": 30,
        "adjustments": adjustments,
        "evidence_count": len(evidence_items),
        "source_url_count": len(evidence_urls),
        "signal_count": len(signals),
        "score": score,
    }


def calculate_persona_score(campaign_brief: dict, research_report: dict, signal_report: dict) -> tuple[int, dict]:
    score = 60
    adjustments: list[str] = []
    target_personas = _campaign_personas(campaign_brief)
    evidence_text = _combined_text(
        research_report.get("company_summary"),
        research_report.get("business_model"),
        signal_report.get("why_now"),
        *[item.get("evidence") for item in research_report.get("evidence") or []],
        *[item.get("description") for item in signal_report.get("signals") or []],
    )

    for persona in target_personas:
        lowered = persona.lower()
        if "cto" in lowered:
            score += 10
            adjustments.append("Campaign targets CTO")
        elif "vp engineering" in lowered:
            score += 10
            adjustments.append("Campaign targets VP Engineering")
        elif "head of platform" in lowered:
            score += 10
            adjustments.append("Campaign targets Head of Platform")

    if any(
        keyword in evidence_text
        for keyword in ["engineering", "developers", "infrastructure", "platform", "security", "data", "growth", "product", "operations"]
    ):
        score += 10
        adjustments.append("Evidence suggests a relevant operating persona")

    if not recommend_persona(campaign_brief, research_report, signal_report):
        score -= 10
        adjustments.append("No clear persona could be inferred")

    if _business_model_unclear(research_report.get("business_model")):
        score -= 10
        adjustments.append("Company category is unclear")

    score = clamp_score(score)
    return score, {
        "base": 60,
        "adjustments": adjustments,
        "target_personas": target_personas,
        "score": score,
    }


def build_score_report(
    account: dict,
    campaign_brief: dict,
    icp: dict,
    research_report: dict,
    signal_report: dict,
) -> dict:
    fit_score, fit_breakdown = calculate_fit_score(research_report, campaign_brief, icp)
    timing_score, timing_breakdown = calculate_timing_score(signal_report)
    confidence_score, confidence_breakdown = calculate_confidence_score(research_report, signal_report)
    persona_score, persona_breakdown = calculate_persona_score(campaign_brief, research_report, signal_report)
    overall_score = calculate_overall_score(fit_score, timing_score, confidence_score, persona_score)
    recommended_persona = recommend_persona(campaign_brief, research_report, signal_report)
    sales_angle = generate_sales_angle(campaign_brief, research_report, signal_report)

    score_explanation = (
        f"{account['company_name']} scored {overall_score} overall based on fit {fit_score}, timing {timing_score}, "
        f"confidence {confidence_score}, and persona alignment {persona_score}. "
        f"The strongest outreach angle is {sales_angle.lower()}."
    )

    return {
        "company_name": account["company_name"],
        "domain": account["domain"],
        "fit_score": fit_score,
        "timing_score": timing_score,
        "confidence_score": confidence_score,
        "persona_score": persona_score,
        "overall_score": overall_score,
        "recommended_persona": recommended_persona,
        "sales_angle": sales_angle,
        "score_explanation": score_explanation,
        "score_breakdown": {
            "fit": fit_breakdown,
            "timing": timing_breakdown,
            "confidence": confidence_breakdown,
            "persona": persona_breakdown,
        },
    }


def _campaign_personas(campaign_brief: dict) -> list[str]:
    raw = campaign_brief.get("target_persona", "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _combined_text(*parts: str | None) -> str:
    return " ".join((part or "").lower() for part in parts if part)


def _business_model_matches_icp(business_model: str | None, icp_text: str) -> bool:
    model = (business_model or "").lower()
    if not model:
        return False
    if "saas" in model and any(term in icp_text for term in ["saas", "software", "platform", "developer"]):
        return True
    return any(term in model and term in icp_text for term in ["software", "platform", "developer", "analytics"])


def _company_category_relevant(evidence_text: str, campaign_brief: dict, icp_text: str) -> bool:
    product_context = _combined_text(
        campaign_brief.get("product_description"),
        campaign_brief.get("pain_statement"),
        campaign_brief.get("ideal_customer_profile"),
    )
    relevant_terms = [
        "engineering",
        "developer",
        "product",
        "analytics",
        "platform",
        "security",
        "compliance",
        "workflow",
        "review",
        "growth",
    ]
    return any(term in evidence_text and (term in product_context or term in icp_text) for term in relevant_terms)


def _has_risk(risks: list[dict], needle: str) -> bool:
    lowered = needle.lower()
    return any(lowered in _combined_text(item.get("risk"), item.get("reason")) for item in risks)


def _business_model_unclear(business_model: str | None) -> bool:
    model = (business_model or "").lower()
    return not model or "unclear" in model or "inconclusive" in model


def _mostly_inference(research_report: dict) -> bool:
    summary = (research_report.get("company_summary") or "").lower()
    evidence_items = research_report.get("evidence") or []
    fit_claims = research_report.get("fit_claims") or []
    inferred_model = (research_report.get("business_model") or "").lower()
    return (
        len(evidence_items) <= 1
        and ("inferred" in inferred_model or "inconclusive" in summary or not fit_claims)
    )
