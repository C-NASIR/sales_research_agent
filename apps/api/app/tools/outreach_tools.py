from __future__ import annotations

from app.tools.persona_tools import recommend_persona


def generate_sales_angle(
    campaign_brief: dict,
    research_report: dict,
    signal_report: dict,
    score_report: dict | None = None,
) -> str:
    pain_text = _combined_text(campaign_brief.get("pain_statement"))
    evidence_text = _combined_text(
        research_report.get("company_summary"),
        research_report.get("business_model"),
        *[item.get("evidence") for item in research_report.get("evidence") or []],
        *[item.get("description") for item in signal_report.get("signals") or []],
    )

    if "review" in pain_text or "code quality" in pain_text:
        return "Code review velocity" if "shipping" in evidence_text or "release" in evidence_text else "Engineering workflow quality"
    if any(keyword in pain_text for keyword in ["security", "compliance"]):
        return "Security and compliance readiness"
    if any(keyword in pain_text for keyword in ["analytics", "experimentation", "conversion"]):
        return "Product analytics visibility"
    if any(keyword in pain_text for keyword in ["growth", "pipeline", "revenue"]):
        return "Growth conversion insight"
    if any(keyword in evidence_text for keyword in ["security", "compliance"]):
        return "Security and compliance readiness"
    if any(keyword in evidence_text for keyword in ["analytics", "product", "experimentation", "activation"]):
        return "Product analytics visibility"
    if any(keyword in evidence_text for keyword in ["growth", "pipeline", "sales", "revenue"]):
        return "Growth conversion insight"
    if any(keyword in evidence_text for keyword in ["platform", "workflow", "operations", "internal tools"]):
        return "Operational workflow automation"
    if any(keyword in evidence_text for keyword in ["developer", "developers", "engineering", "code"]):
        return "Developer experience improvement"
    return "Operational workflow improvement"


def select_personalization_source(research_report: dict, signal_report: dict) -> dict | None:
    evidence_items = research_report.get("evidence") or []
    for item in evidence_items:
        if item.get("source_url") and item.get("confidence") in {"high", "medium"}:
            return {
                "text": item.get("evidence") or item.get("claim") or "Source-backed company observation.",
                "url": item.get("source_url"),
                "label": f"{item.get('source_title') or 'Public source'} evidence from research.",
            }

    signals = signal_report.get("signals") or []
    for item in signals:
        if item.get("source_url") and item.get("confidence") in {"high", "medium"}:
            return {
                "text": item.get("description") or "Signal-backed company observation.",
                "url": item.get("source_url"),
                "label": f"{item.get('type', 'Public signal').replace('_', ' ')} from public research.",
            }
    return None


def build_outreach_subject(company_name: str, sales_angle: str) -> str:
    return f"{sales_angle} at {company_name}"[:120]


def build_outreach_body(
    company_name: str,
    campaign_brief: dict,
    research_report: dict,
    signal_report: dict,
    score_report: dict,
) -> str:
    personalization = select_personalization_source(research_report, signal_report)
    company_context = _market_context(research_report, signal_report)
    pain_statement = (campaign_brief.get("pain_statement") or "operational workflow drag").strip().rstrip(".")
    product_description = (campaign_brief.get("product_description") or "our workflow tooling").strip().rstrip(".")
    confidence = research_report.get("confidence", 0) or 0

    if personalization and confidence >= 50:
        observation = _clean_snippet(personalization["text"])
        first_paragraph = (
            f"Hi there,\n\n"
            f"I came across {company_name} while researching {company_context}. "
            f"One public source suggests {observation}."
        )
    else:
        first_paragraph = (
            f"Hi there,\n\n"
            f"I came across {company_name} while researching companies in this market."
        )

    second_paragraph = (
        f"We help teams dealing with {pain_statement.lower()} using {product_description.lower()}."
    )
    cta = "Worth comparing notes?"
    body = f"{first_paragraph}\n\n{second_paragraph}\n\n{cta}"
    words = body.split()
    if len(words) > 120:
        body = " ".join(words[:120]).rstrip(".") + "?"
    return body


def build_outreach_draft(
    account: dict,
    campaign_brief: dict,
    research_report: dict,
    signal_report: dict,
    score_report: dict,
) -> dict:
    personalization = select_personalization_source(research_report, signal_report)
    sales_angle = score_report.get("sales_angle") or generate_sales_angle(campaign_brief, research_report, signal_report, score_report)
    body = build_outreach_body(account["company_name"], campaign_brief, research_report, signal_report, score_report)
    risk_notes: list[str] = []
    if not personalization:
        risk_notes.append("No strong source backed personalization was available.")
    if (research_report.get("confidence", 0) or 0) < 50:
        risk_notes.append("Research confidence is low, so outreach wording stays cautious.")
    if "simulated" in (research_report.get("company_summary") or "").lower():
        risk_notes.append("Draft is anchored to simulated research rather than verified public evidence.")

    return {
        "company_name": account["company_name"],
        "domain": account["domain"],
        "subject": build_outreach_subject(account["company_name"], sales_angle),
        "body": body,
        "personalization_source": personalization["label"] if personalization else "",
        "personalization_source_url": personalization["url"] if personalization else None,
        "sales_angle": sales_angle,
        "risk_notes": risk_notes,
        "recommended_persona": recommend_persona(campaign_brief, research_report, signal_report),
    }


def _market_context(research_report: dict, signal_report: dict) -> str:
    evidence_text = _combined_text(
        research_report.get("company_summary"),
        research_report.get("business_model"),
        signal_report.get("why_now"),
        *[item.get("evidence") for item in research_report.get("evidence") or []],
    )
    if any(keyword in evidence_text for keyword in ["developer", "engineering", "platform", "infrastructure"]):
        return "developer-focused software teams"
    if any(keyword in evidence_text for keyword in ["product", "analytics", "experimentation", "conversion"]):
        return "product-led software teams"
    if any(keyword in evidence_text for keyword in ["growth", "revenue", "sales", "pipeline"]):
        return "growth-focused teams"
    return "teams in this market"


def _clean_snippet(value: str) -> str:
    cleaned = " ".join(value.strip().split())
    cleaned = cleaned[:140].rstrip(" ,.;:")
    if not cleaned:
        return "there is a relevant public company signal"
    if cleaned[0].isupper():
        return cleaned
    return cleaned


def _combined_text(*parts: str | None) -> str:
    return " ".join((part or "").lower() for part in parts if part)
