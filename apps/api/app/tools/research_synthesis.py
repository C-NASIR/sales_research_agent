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
        summary = (
            f"Public web research suggests {account['company_name']} has a relevant product or workflow footprint. "
            f"This summary is grounded in public pages and search results collected in Phase 4."
        )
        business_model = _infer_business_model(evidence_items)
        risks = []
    else:
        summary = (
            f"Public research for {account['company_name']} was inconclusive in Phase 4. "
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
        if evidence_type == "careers":
            signals.append(
                {
                    "type": "hiring_signal",
                    "description": "A careers or jobs page was found during research.",
                    "why_it_matters": "Active hiring can indicate team growth or ongoing operational investment.",
                    "source_url": item["source_url"],
                    "confidence": item["confidence"],
                }
            )
        elif evidence_type in {"blog", "engineering"}:
            signals.append(
                {
                    "type": "engineering_activity",
                    "description": "Engineering or blog content was found on public sources.",
                    "why_it_matters": "Recent engineering content can indicate ongoing product and team activity.",
                    "source_url": item["source_url"],
                    "confidence": item["confidence"],
                }
            )
        elif evidence_type == "pricing":
            signals.append(
                {
                    "type": "business_model_signal",
                    "description": "A pricing page was identified.",
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
                        "description": "A search snippet mentioned funding, but the claim was not verified by a scraped page.",
                        "why_it_matters": "Funding can indicate momentum, but this signal remains low confidence until verified.",
                        "source_url": result["url"],
                        "confidence": "low",
                    }
                )
                break

    source_summaries = _build_source_summaries(search_results, scraped_sources)
    if signals:
        timing_score = min(85, 45 + len(signals) * 10)
        why_now = "Public sources suggest some current commercial or engineering activity worth a cautious outbound test."
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
