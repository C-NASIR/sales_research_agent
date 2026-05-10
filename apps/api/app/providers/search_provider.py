from __future__ import annotations

import os
from collections import OrderedDict

from tenacity import retry, stop_after_attempt, wait_fixed

from app.config import settings
from app.schemas.source import SearchResult


class SearchProviderError(RuntimeError):
    pass


def ensure_search_provider_ready() -> None:
    if settings.workflow_provider_mode == "stub":
        return
    if not settings.tavily_api_key:
        raise SearchProviderError("TAVILY_API_KEY is required for real workflow mode")


def search_company_web(company_name: str, domain: str, queries: list[str], max_results: int) -> list[SearchResult]:
    if settings.workflow_provider_mode == "stub":
        behavior = os.getenv("STUB_SEARCH_BEHAVIOR", "success").strip().lower()
        if behavior == "error":
            raise SearchProviderError("Stub search failure")
        if behavior == "empty":
            return []
        return _build_stub_results(company_name, domain, max_results)

    try:
        from tavily import TavilyClient
    except Exception as exc:
        raise SearchProviderError("tavily-python is not installed or failed to import") from exc

    client = TavilyClient(api_key=settings.tavily_api_key)
    per_query_limit = max(1, min(2, max_results))
    ordered_results: OrderedDict[str, SearchResult] = OrderedDict()

    for query in queries:
        response = _run_search(client, query, per_query_limit)
        for item in response.get("results", []):
            url = (item.get("url") or "").strip()
            if not url or url in ordered_results:
                continue
            ordered_results[url] = SearchResult(
                title=(item.get("title") or url).strip(),
                url=url,
                snippet=(item.get("content") or item.get("snippet") or "").strip() or None,
            )
            if len(ordered_results) >= max_results:
                return list(ordered_results.values())

    return list(ordered_results.values())


@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=True)
def _run_search(client, query: str, max_results: int) -> dict:
    response = client.search(
        query,
        max_results=max_results,
        include_raw_content=False,
        search_depth="basic",
    )
    if not isinstance(response, dict):
        raise SearchProviderError("Unexpected Tavily response shape")
    return response


def _build_stub_results(company_name: str, domain: str, max_results: int) -> list[SearchResult]:
    candidates = [
        SearchResult(
            title=f"{company_name} homepage",
            url=f"https://{domain}",
            snippet=f"{company_name} sells workflow software for engineering teams.",
            source="stub_search",
        ),
        SearchResult(
            title=f"{company_name} pricing",
            url=f"https://{domain}/pricing",
            snippet=f"{company_name} lists pricing for teams and enterprise buyers.",
            source="stub_search",
        ),
        SearchResult(
            title=f"{company_name} careers",
            url=f"https://{domain}/careers",
            snippet=f"{company_name} is hiring engineers and platform roles.",
            source="stub_search",
        ),
        SearchResult(
            title=f"{company_name} engineering blog",
            url=f"https://{domain}/engineering",
            snippet=f"{company_name} publishes engineering posts about developer workflows.",
            source="stub_search",
        ),
    ]
    return candidates[:max_results]
