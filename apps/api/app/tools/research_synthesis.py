from __future__ import annotations

from collections import OrderedDict
from typing import Any


def synthesize_research_report(
    account: dict,
    campaign_brief: dict,
    icp: dict,
    search_results: list[dict],
    scraped_sources: list[dict],
    evidence_items: list[dict],
) -> dict:
    source_summaries = _build_source_summaries(search_results, scraped_sources)
    fit_claims = evidence_items[:3]
    confidence = _research_confidence(evidence_items)

    if evidence_items:
        top_evidence = "; ".join(_clean_evidence(item.get("evidence", "")) for item in evidence_items[:2])
        summary = (
            f"Public research indicates {account['company_name']} has a relevant software or workflow footprint. "
            f"Key evidence includes {top_evidence}."
        )
        business_model = _infer_business_model(evidence_items)
        risks = _build_research_risks(source_summaries, evidence_items, confidence)
    else:
        summary = (
            f"Public research for {account['company_name']} was inconclusive. "
            "The account may still be relevant, but the current evidence base is weak."
        )
        business_model = "Inconclusive from public sources"
        risks = [
            {
                "risk": "Insufficient public evidence",
                "reason": "Search and scrape outputs did not produce enough source-backed detail to support strong claims.",
                "confidence": "high",
            }
        ]

    return {
        "company_name": account["company_name"],
        "domain": account["domain"],
        "company_summary": summary,
        "business_model": business_model,
        "fit_claims": fit_claims,
        "evidence": evidence_items[:5],
        "risks": risks,
        "confidence": confidence,
        "sources": source_summaries,
    }


def synthesize_signal_report(
    account: dict,
    campaign_brief: dict,
    icp: dict,
    search_results: list[dict],
    scraped_sources: list[dict],
    evidence_items: list[dict],
) -> dict:
    signals: list[dict] = []
    for item in evidence_items:
        evidence_type = item.get("evidence_type", "unknown")
        snippet = _clean_evidence(item.get("evidence", ""))
        if evidence_type == "careers":
            signals.append(
                {
                    "type": "hiring_signal",
                    "description": f"Public hiring evidence: {snippet}",
                    "why_it_matters": "Active hiring can indicate team growth or ongoing operational investment.",
                    "source_url": item["source_url"],
                    "confidence": item["confidence"],
                }
            )
        elif evidence_type in {"blog", "engineering"}:
            signals.append(
                {
                    "type": "engineering_activity",
                    "description": f"Engineering activity evidence: {snippet}",
                    "why_it_matters": "Recent engineering content can indicate ongoing product and team activity.",
                    "source_url": item["source_url"],
                    "confidence": item["confidence"],
                }
            )
        elif evidence_type == "pricing":
            signals.append(
                {
                    "type": "business_model_signal",
                    "description": f"Commercial evidence: {snippet}",
                    "why_it_matters": "Pricing information helps confirm product packaging and commercial intent.",
                    "source_url": item["source_url"],
                    "confidence": item["confidence"],
                }
            )

    if not signals:
        for result in search_results:
            snippet = (result.get("snippet") or "").lower()
            if "funding" in snippet:
                signals.append(
                    {
                        "type": "funding_signal",
                        "description": f"Unverified funding reference from search: {_clean_evidence(result.get('snippet') or '')}",
                        "why_it_matters": "Funding can indicate momentum, but this signal remains low confidence until verified.",
                        "source_url": result["url"],
                        "confidence": "low",
                    }
                )
                break

    source_summaries = _build_source_summaries(search_results, scraped_sources)
    if signals:
        timing_score = min(85, 45 + len(signals) * 10)
        why_now = _build_why_now(signals)
        confidence = 70 if any(signal["confidence"] == "high" for signal in signals) else 55
    else:
        timing_score = 30
        why_now = "No clear timing signal was found in public sources, so urgency remains uncertain."
        confidence = 25

    return {
        "company_name": account["company_name"],
        "domain": account["domain"],
        "signals": signals,
        "timing_score": timing_score,
        "why_now": why_now,
        "confidence": confidence,
        "sources": source_summaries,
    }


def build_low_confidence_reports(
    account: dict,
    reason: str,
    *,
    search_results: list[dict] | None = None,
    scraped_sources: list[dict] | None = None,
) -> tuple[dict, dict]:
    search_results = search_results or []
    scraped_sources = scraped_sources or []
    source_summaries = _build_source_summaries(search_results, scraped_sources)
    research_report = {
        "company_name": account["company_name"],
        "domain": account["domain"],
        "company_summary": f"Public research for {account['company_name']} was inconclusive. {reason}",
        "business_model": "Inconclusive from public sources",
        "fit_claims": [],
        "evidence": [],
        "risks": [
            {
                "risk": "Insufficient evidence",
                "reason": reason,
                "confidence": "high",
            }
        ],
        "confidence": 20,
        "sources": source_summaries,
    }
    signal_report = {
        "company_name": account["company_name"],
        "domain": account["domain"],
        "signals": [],
        "timing_score": 20,
        "why_now": "No reliable timing signal could be established from the available public sources.",
        "confidence": 20,
        "sources": source_summaries,
    }
    return research_report, signal_report


def _build_source_summaries(search_results: list[dict], scraped_sources: list[dict]) -> list[dict]:
    ordered: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for result in search_results:
        url = result.get("url")
        if url and url not in ordered:
            ordered[url] = {
                "url": url,
                "title": result.get("title"),
                "source": result.get("source", "tavily"),
            }
    for source in scraped_sources:
        if not source.get("success"):
            continue
        url = source.get("url")
        if url and url not in ordered:
            ordered[url] = {
                "url": url,
                "title": source.get("title"),
                "source": source.get("source", "scrape"),
            }
    return list(ordered.values())


def _research_confidence(evidence_items: list[dict]) -> int:
    if not evidence_items:
        return 20
    high_count = sum(1 for item in evidence_items if item.get("confidence") == "high")
    medium_count = sum(1 for item in evidence_items if item.get("confidence") == "medium")
    return min(85, 35 + high_count * 15 + medium_count * 10 + max(0, len(evidence_items) - high_count - medium_count) * 5)


def _infer_business_model(evidence_items: list[dict]) -> str:
    text = " ".join(item.get("evidence", "").lower() for item in evidence_items)
    if any(keyword in text for keyword in ["pricing", "platform", "product", "developers", "enterprise"]):
        return "B2B SaaS"
    if "open source" in text:
        return "Open source with commercial offering"
    return "Software business inferred from public sources"


def _clean_evidence(value: str) -> str:
    cleaned = " ".join(value.split())
    cleaned = cleaned[:160].rstrip(" ,.;:")
    if not cleaned:
        return "limited public evidence"
    return cleaned.lower()


def _build_why_now(signals: list[dict]) -> str:
    descriptions = [signal["description"] for signal in signals[:2] if signal.get("description")]
    if not descriptions:
        return "Public sources suggest some current activity worth a cautious outbound test."
    return f"Public sources suggest current activity worth testing because {descriptions[0].rstrip('.')}."


def _build_research_risks(source_summaries: list[dict], evidence_items: list[dict], confidence: int) -> list[dict]:
    risks: list[dict] = []
    if len(source_summaries) <= 1:
        risks.append(
            {
                "risk": "Limited source diversity",
                "reason": "Most conclusions come from a narrow set of public pages.",
                "confidence": "medium",
            }
        )
    if len(evidence_items) <= 1 or confidence < 50:
        risks.append(
            {
                "risk": "Thin public evidence",
                "reason": "The current evidence base is usable but still limited for strong personalization.",
                "confidence": "medium",
            }
        )
    return risks
