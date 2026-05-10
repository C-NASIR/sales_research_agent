from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.providers.scrape_provider import ensure_scrape_provider_ready
from app.providers.search_provider import SearchProviderError, ensure_search_provider_ready
from app.providers.structured_llm import StructuredGenerationError, ensure_structured_llm_ready
from app.tools.research_synthesis import build_low_confidence_reports, synthesize_research_report, synthesize_signal_report
from app.tools.source_extraction import build_evidence_items
from app.tools.web_scrape import scrape_company_sources
from app.tools.web_search import SearchError, search_company_web

_RESEARCH_CONTEXT_CACHE: dict[tuple[str, str], dict] = {}


class ResearchConfigurationError(RuntimeError):
    pass


@dataclass
class ResearchContext:
    search_results: list[dict]
    scraped_sources: list[dict]
    evidence_items: list[dict]


def ensure_real_research_ready() -> None:
    if settings.research_mode != "real":
        raise ResearchConfigurationError("RESEARCH_MODE only supports 'real'")
    try:
        ensure_search_provider_ready()
        ensure_scrape_provider_ready()
        ensure_structured_llm_ready()
    except (SearchProviderError, StructuredGenerationError, RuntimeError) as exc:
        raise ResearchConfigurationError(str(exc)) from exc


def get_cached_research_context(account: dict) -> ResearchContext | None:
    raw = _RESEARCH_CONTEXT_CACHE.get((account["company_name"], account["domain"]))
    if raw is None:
        return None
    return ResearchContext(**raw)


def run_real_account_research(
    account: dict,
    campaign_brief: dict,
    icp: dict,
) -> tuple[dict, dict]:
    ensure_real_research_ready()

    search_results = [item.model_dump(mode="json") for item in search_company_web(
        account["company_name"],
        account["domain"],
        settings.max_search_results,
    )]

    urls = _prioritized_urls(account["domain"], search_results)
    scraped_sources = [
        item.model_dump(mode="json")
        for item in scrape_company_sources(urls, settings.max_scraped_pages_per_account)
    ]

    evidence_items = build_evidence_items(
        account["company_name"],
        account["domain"],
        [
            _scraped_source_from_dict(item)
            for item in scraped_sources
        ],
        campaign_brief,
        icp,
    )

    if not search_results and not scraped_sources:
        research_report, signal_report = build_low_confidence_reports(
            account,
            "Search and scrape returned no usable public sources.",
            search_results=search_results,
            scraped_sources=scraped_sources,
        )
    else:
        research_report = synthesize_research_report(
            account,
            campaign_brief,
            icp,
            search_results,
            scraped_sources,
            evidence_items,
        )
        signal_report = synthesize_signal_report(
            account,
            campaign_brief,
            icp,
            search_results,
            scraped_sources,
            evidence_items,
        )
        if not evidence_items:
            research_report, signal_report = build_low_confidence_reports(
                account,
                "Public sources were found but did not yield strong evidence snippets.",
                search_results=search_results,
                scraped_sources=scraped_sources,
            )

    _RESEARCH_CONTEXT_CACHE[(account["company_name"], account["domain"])] = {
        "search_results": search_results,
        "scraped_sources": scraped_sources,
        "evidence_items": evidence_items,
    }
    return research_report, signal_report


def _prioritized_urls(domain: str, search_results: list[dict]) -> list[str]:
    homepage = f"https://{domain}"
    urls = [homepage]
    urls.extend(item["url"] for item in search_results if item.get("url"))
    return urls


def _scraped_source_from_dict(item: dict):
    from app.schemas.source import ScrapedSource

    return ScrapedSource.model_validate(item)
