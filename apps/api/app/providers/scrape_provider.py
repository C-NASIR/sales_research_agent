from __future__ import annotations

import os
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

from app.config import settings
from app.schemas.source import ScrapedSource

PREFERRED_URL_HINTS = [
    "about",
    "pricing",
    "careers",
    "jobs",
    "blog",
    "engineering",
    "product",
    "customers",
]


class ScrapeProviderError(RuntimeError):
    pass


def ensure_scrape_provider_ready() -> None:
    if settings.workflow_provider_mode == "stub":
        return
    if not settings.firecrawl_api_key:
        raise ScrapeProviderError("FIRECRAWL_API_KEY is required for real workflow mode")


def scrape_company_sources(urls: list[str], max_pages: int) -> list[ScrapedSource]:
    deduped = _dedupe_urls(urls)
    prioritized = sorted(deduped, key=_url_priority)
    return [scrape_url(url) for url in prioritized[:max_pages]]


def scrape_url(url: str) -> ScrapedSource:
    if settings.workflow_provider_mode == "stub":
        behavior = os.getenv("STUB_SCRAPE_BEHAVIOR", "success").strip().lower()
        if behavior == "error":
            return ScrapedSource(url=url, source="stub_scrape", success=False, error="Stub scrape failure")
        return _build_stub_source(url)

    firecrawl_result = _try_firecrawl(url)
    if firecrawl_result is not None:
        return firecrawl_result
    return _httpx_fallback(url)


def _dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for url in urls:
        normalized = url.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _url_priority(url: str) -> tuple[int, int, str]:
    parsed = urlparse(url)
    path = (parsed.path or "/").lower()
    is_homepage = 0 if path in {"", "/"} else 1
    hint_rank = len(PREFERRED_URL_HINTS)
    for index, hint in enumerate(PREFERRED_URL_HINTS):
        if hint in url.lower():
            hint_rank = index
            break
    return (is_homepage, hint_rank, url)


def _try_firecrawl(url: str) -> ScrapedSource | None:
    try:
        try:
            from firecrawl import Firecrawl

            client = Firecrawl(api_key=settings.firecrawl_api_key)
            response = _firecrawl_scrape(client, url)
        except Exception:
            from firecrawl import FirecrawlApp

            client = FirecrawlApp(api_key=settings.firecrawl_api_key)
            response = _firecrawl_scrape_app(client, url)
    except Exception:
        return None

    markdown = _extract_mapping_value(response, ["markdown", "data.markdown"])
    title = _extract_mapping_value(response, ["metadata.title", "title"])
    text = _extract_mapping_value(response, ["text", "data.text"])
    if markdown or text:
        return ScrapedSource(
            url=url,
            title=title,
            markdown=_truncate(markdown),
            text=_truncate(text),
            source="firecrawl",
            success=True,
        )
    return None


@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=True)
def _firecrawl_scrape(client, url: str):
    return client.scrape(url, formats=["markdown"])


@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=True)
def _firecrawl_scrape_app(client, url: str):
    return client.scrape_url(url, params={"formats": ["markdown"]})


def _httpx_fallback(url: str) -> ScrapedSource:
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else None
        text = " ".join(chunk.strip() for chunk in soup.stripped_strings if chunk.strip())
        return ScrapedSource(
            url=str(response.url),
            title=title,
            text=_truncate(text),
            source="httpx_fallback",
            success=True,
        )
    except Exception as exc:
        return ScrapedSource(
            url=url,
            source="httpx_fallback",
            success=False,
            error=str(exc),
        )


def _extract_mapping_value(payload, candidate_paths: list[str]) -> str | None:
    if isinstance(payload, str):
        return payload
    for path in candidate_paths:
        value = payload
        for segment in path.split("."):
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(segment)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _truncate(value: str | None) -> str | None:
    if value is None:
        return None
    return value[: settings.max_source_chars].strip()


def _build_stub_source(url: str) -> ScrapedSource:
    parsed = urlparse(url)
    host = parsed.netloc or "example.com"
    path = (parsed.path or "/").lower()
    if path in {"", "/"}:
        title = f"{host} homepage"
        text = (
            f"{host} provides software for engineering teams. "
            "The platform helps developer organizations improve review workflows, security, and delivery quality."
        )
    elif "pricing" in path:
        title = f"{host} pricing"
        text = "Pricing includes team and enterprise plans for developer organizations and platform teams."
    elif "careers" in path or "jobs" in path:
        title = f"{host} careers"
        text = "The company is hiring platform engineers, product engineers, and developer experience roles."
    elif "engineering" in path or "blog" in path:
        title = f"{host} engineering"
        text = "Engineering posts describe platform reliability, code review practices, and developer workflow improvements."
    else:
        title = f"{host} page"
        text = "This page describes the product, platform, and customer workflow."
    return ScrapedSource(
        url=url,
        title=title,
        text=_truncate(text),
        source="stub_scrape",
        success=True,
    )
