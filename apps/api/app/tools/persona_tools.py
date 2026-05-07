from __future__ import annotations


def recommend_persona(campaign_brief: dict, research_report: dict, signal_report: dict) -> str:
    personas = [item.strip() for item in campaign_brief.get("target_persona", "").split(",") if item.strip()]
    evidence_text = _combined_text(
        research_report.get("company_summary"),
        research_report.get("business_model"),
        signal_report.get("why_now"),
        *[item.get("evidence") for item in research_report.get("evidence") or []],
        *[item.get("description") for item in signal_report.get("signals") or []],
    )

    inferred = _infer_persona_from_text(evidence_text)
    if personas:
        best = _best_campaign_persona(personas, inferred, evidence_text)
        if best:
            return best
        return personas[0]

    if inferred:
        return inferred
    return "Founder or Operator"


def _infer_persona_from_text(text: str) -> str | None:
    if any(keyword in text for keyword in ["engineering", "code", "developers", "platform", "infrastructure", "security", "reliability"]):
        return "VP Engineering"
    if any(keyword in text for keyword in ["product analytics", "activation", "growth", "conversion", "experimentation"]):
        return "Head of Product"
    if any(keyword in text for keyword in ["revenue", "pipeline", "sales", "go to market", "customer growth"]):
        return "Head of Growth"
    return None


def _best_campaign_persona(personas: list[str], inferred: str | None, text: str) -> str | None:
    best_persona: str | None = None
    best_score = -1
    for persona in personas:
        score = 0
        lowered = persona.lower()
        if inferred and inferred.lower() in lowered:
            score += 5
        if "vp engineering" in lowered and any(
            keyword in text for keyword in ["engineering", "developers", "platform", "infrastructure", "security", "reliability"]
        ):
            score += 4
        if "cto" in lowered and any(
            keyword in text for keyword in ["engineering", "platform", "security", "architecture", "developer"]
        ):
            score += 3
        if "head of platform" in lowered and any(
            keyword in text for keyword in ["platform", "infrastructure", "operations", "internal tools"]
        ):
            score += 4
        if "head of product" in lowered and any(
            keyword in text for keyword in ["product", "analytics", "experimentation", "conversion"]
        ):
            score += 4
        if "head of growth" in lowered and any(
            keyword in text for keyword in ["growth", "pipeline", "revenue", "customer growth"]
        ):
            score += 4
        if score > best_score:
            best_persona = persona
            best_score = score
    return best_persona


def _combined_text(*parts: str | None) -> str:
    return " ".join((part or "").lower() for part in parts if part)
