from __future__ import annotations

from collections import OrderedDict

from tenacity import retry, stop_after_attempt, wait_fixed

from app.config import settings
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
    if not settings.tavily_api_key:
        raise SearchError("TAVILY_API_KEY is required for real research mode")

    try:
        from tavily import TavilyClient
    except Exception as exc:
        raise SearchError("tavily-python is not installed or failed to import") from exc

    client = TavilyClient(api_key=settings.tavily_api_key)
    per_query_limit = max(1, min(2, max_results))
    ordered_results: OrderedDict[str, SearchResult] = OrderedDict()

    for query in build_company_search_queries(company_name, domain):
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

    if not ordered_results:
        raise SearchError(f"No search results returned for {company_name} ({domain})")

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
        raise SearchError("Unexpected Tavily response shape")
    return response
