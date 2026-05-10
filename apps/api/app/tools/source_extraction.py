from __future__ import annotations

from urllib.parse import urlparse

from app.schemas.source import ScrapedSource

KEYWORDS = [
    "pricing",
    "enterprise",
    "customers",
    "developers",
    "engineering",
    "platform",
    "security",
    "compliance",
    "open source",
    "careers",
    "hiring",
    "jobs",
    "growth",
    "product",
    "analytics",
    "workflow",
    "code",
    "review",
]


def extract_title(source: ScrapedSource) -> str | None:
    return source.title


def classify_source_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for evidence_type in ["pricing", "careers", "jobs", "blog", "docs", "about", "product", "engineering"]:
        if evidence_type in path:
            return "careers" if evidence_type == "jobs" else evidence_type
    if path in {"", "/"}:
        return "homepage"
    return "unknown"


def extract_relevant_snippets(source: ScrapedSource, keywords: list[str], max_snippets: int = 5) -> list[str]:
    body = source.markdown or source.text or ""
    if not body:
        return []
    snippets: list[str] = []
    for line in body.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if any(keyword.lower() in lowered for keyword in keywords):
            snippets.append(normalized[:280])
        if len(snippets) >= max_snippets:
            break
    return snippets


def build_evidence_items(
    company_name: str,
    domain: str,
    sources: list[ScrapedSource],
    campaign_brief: dict,
    icp: dict,
) -> list[dict]:
    keywords = KEYWORDS + [company_name.lower(), domain.lower()]
    keywords.extend(_tokenize_keywords(campaign_brief.get("product_description")))
    keywords.extend(_tokenize_keywords(campaign_brief.get("pain_statement")))
    keywords.extend(_tokenize_keywords(campaign_brief.get("ideal_customer_profile")))
    for item in icp.get("positive_signals") or []:
        keywords.extend(_tokenize_keywords(item))
    evidence_items: list[dict] = []
    for source in sources:
        if not source.success:
            continue
        evidence_type = classify_source_url(source.url)
        snippets = extract_relevant_snippets(source, keywords, max_snippets=3)
        for snippet in snippets:
            evidence_items.append(
                {
                    "claim": f"{company_name} has publicly visible information related to {evidence_type}.",
                    "evidence": snippet,
                    "source_url": source.url,
                    "source_title": extract_title(source),
                    "confidence": "high" if evidence_type in {"homepage", "pricing", "product", "engineering"} else "medium",
                    "evidence_type": evidence_type,
                }
            )
    return evidence_items


def _tokenize_keywords(value: str | None) -> list[str]:
    if not value:
        return []
    return [token.lower() for token in value.replace(",", " ").split() if len(token) >= 4]
