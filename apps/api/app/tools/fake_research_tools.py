from __future__ import annotations


KNOWN_COMPANIES = {
    "sentry": {
        "summary": "developer focused software company centered on application reliability and engineering quality",
        "business_model": "B2B SaaS",
        "sales_angle": "Engineering workflow quality",
        "recommended_persona": "VP Engineering",
        "timing_signal": "Teams operating developer tooling often revisit review quality as code volume grows.",
    },
    "posthog": {
        "summary": "product analytics and experimentation platform used by technical product teams",
        "business_model": "B2B SaaS",
        "sales_angle": "Faster product and engineering iteration",
        "recommended_persona": "Head of Engineering",
        "timing_signal": "Product-led teams often care about keeping delivery quality high while shipping quickly.",
    },
    "linear": {
        "summary": "software planning and issue tracking platform for engineering and product organizations",
        "business_model": "B2B SaaS",
        "sales_angle": "Cleaner execution and review discipline",
        "recommended_persona": "VP Engineering",
        "timing_signal": "Teams that prioritize execution velocity often invest in review bottleneck reduction.",
    },
    "retool": {
        "summary": "internal tools platform that helps teams build operational workflows quickly",
        "business_model": "B2B SaaS",
        "sales_angle": "Developer productivity for internal tooling teams",
        "recommended_persona": "Head of Platform",
        "timing_signal": "Platform-oriented teams usually feel review drag across many internal tool changes.",
    },
    "vercel": {
        "summary": "developer platform company focused on frontend delivery and release workflows",
        "business_model": "B2B SaaS",
        "sales_angle": "Release quality for modern web teams",
        "recommended_persona": "CTO",
        "timing_signal": "Release-centric organizations often value consistent review quality for fast-moving teams.",
    },
}


def build_company_profile(company_name: str, domain: str) -> dict[str, str]:
    slug = company_name.strip().lower()
    for known_name, profile in KNOWN_COMPANIES.items():
        if known_name in slug:
            return profile

    return {
        "summary": f"{company_name} is treated as a business software company for the Phase 3 simulated workflow.",
        "business_model": "B2B software",
        "sales_angle": f"Workflow quality for teams at {company_name}",
        "recommended_persona": "VP Engineering",
        "timing_signal": f"The {domain} account may care about efficient team workflows, but this is simulated until Phase 4 research exists.",
    }
