from __future__ import annotations


def detect_fake_familiarity(text: str) -> list[str]:
    lowered = text.lower()
    phrases = [
        "following up",
        "as discussed",
        "our conversation",
        "you asked",
        "circling back",
        "checking back",
        "per your request",
        "as promised",
        "great speaking",
    ]
    return [f"Body contains fake familiarity phrase: {phrase}." for phrase in phrases if phrase in lowered]


def detect_unsupported_claims(outreach_draft: dict, research_report: dict, signal_report: dict) -> list[str]:
    body = (outreach_draft.get("body") or "").lower()
    evidence_text = _combined_text(
        *[item.get("evidence") for item in research_report.get("evidence") or []],
        *[item.get("claim") for item in research_report.get("fit_claims") or []],
        *[item.get("description") for item in signal_report.get("signals") or []],
        signal_report.get("why_now"),
    )
    issues: list[str] = []

    pain_terms = ["struggling", "pain", "suffering", "blocked by"]
    if any(term in body for term in pain_terms) and not any(term in evidence_text for term in pain_terms):
        issues.append("Draft claims a specific pain that is not supported by evidence.")

    if "hiring" in body and not any("hiring" in _combined_text(item.get("description"), item.get("type")) for item in signal_report.get("signals") or []):
        issues.append("Draft mentions hiring without source-backed hiring evidence.")

    if any(term in body for term in ["raised", "funding"]) and not any(
        "funding" in _combined_text(item.get("description"), item.get("type")) for item in signal_report.get("signals") or []
    ):
        issues.append("Draft mentions funding without source-backed funding evidence.")

    if "uses " in body and "uses " not in evidence_text:
        issues.append("Draft claims tool usage without source support.")

    if outreach_draft.get("personalization_source") and not outreach_draft.get("personalization_source_url"):
        issues.append("Draft references personalization but no personalization source URL was saved.")

    return issues


def detect_missing_personalization(outreach_draft: dict) -> list[str]:
    issues: list[str] = []
    if not outreach_draft.get("personalization_source"):
        issues.append("Personalization source is missing.")
    if outreach_draft.get("personalization_source") and not outreach_draft.get("personalization_source_url"):
        issues.append("Personalization source URL is missing.")
    return issues


def detect_deceptive_subject(outreach_draft: dict) -> list[str]:
    subject = (outreach_draft.get("subject") or "").strip()
    lowered = subject.lower()
    body = (outreach_draft.get("body") or "").lower()
    issues: list[str] = []
    for prefix in ["re:", "fwd:", "urgent", "following up"]:
        if prefix in lowered:
            issues.append(f"Subject uses deceptive framing: {prefix}")
    if "quick question" in lowered and "worth comparing notes" in body:
        issues.append("Subject uses 'quick question' for a sales email.")
    return issues


def review_outreach_draft(
    outreach_draft: dict,
    research_report: dict,
    signal_report: dict,
) -> dict:
    blocked_reasons: list[str] = []
    issues: list[str] = []

    if not outreach_draft.get("subject"):
        blocked_reasons.append("Subject is empty.")
    if not outreach_draft.get("body"):
        blocked_reasons.append("Body is empty.")

    fake_familiarity = detect_fake_familiarity(outreach_draft.get("body") or "")
    blocked_reasons.extend(fake_familiarity)
    blocked_reasons.extend(detect_deceptive_subject(outreach_draft))

    unsupported_claims = detect_unsupported_claims(outreach_draft, research_report, signal_report)
    for issue in unsupported_claims:
        if any(keyword in issue.lower() for keyword in ["pain", "hiring", "funding", "tool usage"]):
            blocked_reasons.append(issue)
        else:
            issues.append(issue)

    issues.extend(detect_missing_personalization(outreach_draft))

    evidence_items = research_report.get("evidence") or []
    if not evidence_items:
        issues.append("Research evidence is empty.")
    if any(not item.get("source_url") for item in evidence_items):
        issues.append("At least one evidence item is missing a source URL.")
    if (research_report.get("confidence", 0) or 0) < 50:
        issues.append("Research confidence is low.")
    if not outreach_draft.get("personalization_source_url"):
        issues.append("No source-backed personalization URL was available.")
    if "while researching companies in this market" in (outreach_draft.get("body") or "").lower():
        issues.append("Draft is generic and may need sharper personalization.")

    if blocked_reasons:
        quality_status = "blocked"
    elif issues:
        quality_status = "flagged"
    else:
        quality_status = "approved_by_reviewer"

    recommended_edits: list[str] = []
    if blocked_reasons or issues:
        recommended_edits.append("Anchor the message to one source-backed observation.")
    if any("familiarity" in item.lower() for item in blocked_reasons):
        recommended_edits.append("Remove any language that implies prior contact.")
    if any("personalization" in item.lower() for item in issues + blocked_reasons):
        recommended_edits.append("Add a clear personalization source and URL.")
    if any("confidence" in item.lower() for item in issues):
        recommended_edits.append("Use more cautious wording until evidence quality improves.")

    return {
        "company_name": outreach_draft["company_name"],
        "domain": outreach_draft["domain"],
        "quality_status": quality_status,
        "issues": issues,
        "blocked_reasons": blocked_reasons,
        "recommended_edits": recommended_edits,
    }


def _combined_text(*parts: str | None) -> str:
    return " ".join((part or "").lower() for part in parts if part)


review_outreach_quality = review_outreach_draft
