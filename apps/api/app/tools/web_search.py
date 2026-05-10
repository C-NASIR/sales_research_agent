from __future__ import annotations

from app.providers.search_provider import SearchProviderError, ensure_search_provider_ready
from app.providers.search_provider import search_company_web as provider_search_company_web
from app.schemas.source import SearchResult


class SearchError(RuntimeError):
    pass


def build_company_search_queries(company_name: str, domain: str) -> list[str]:
    return [
        f"{company_name} {domain}",
        f"site:{domain} pricing",
        f"site:{domain} careers OR jobs",
        f"site:{domain} blog engineering",
        f"{company_name} funding product launch",
    ]


def search_company_web(company_name: str, domain: str, max_results: int) -> list[SearchResult]:
    try:
        ensure_search_provider_ready()
        results = provider_search_company_web(
            company_name,
            domain,
            build_company_search_queries(company_name, domain),
            max_results,
        )
    except SearchProviderError as exc:
        raise SearchError(str(exc)) from exc
    if not results:
        raise SearchError(f"No search results returned for {company_name} ({domain})")
    return results
