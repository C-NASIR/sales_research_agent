from __future__ import annotations

from collections.abc import Sequence


def clamp_score(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


def calculate_overall_score(
    fit_score: int,
    timing_score: int,
    confidence_score: int,
    persona_score: int,
) -> int:
    overall = (
        clamp_score(fit_score) * 0.45
        + clamp_score(timing_score) * 0.25
        + clamp_score(confidence_score) * 0.20
        + clamp_score(persona_score) * 0.10
    )
    return clamp_score(round(overall))


def calculate_fit_score(fit_claims: Sequence[dict] | None) -> int:
    claims = fit_claims or []
    score = 50
    for claim in claims:
        if claim.get("confidence") in {"medium", "high"}:
            score += 10
    return clamp_score(min(score, 90))


def calculate_confidence_score(evidence: Sequence[dict] | None) -> int:
    evidence_items = evidence or []
    score = 30
    for item in evidence_items:
        if item.get("source_url"):
            score += 10
    if any(item.get("confidence") == "high" for item in evidence_items):
        score += 10
    return clamp_score(min(score, 95))


def calculate_persona_score(target_personas: Sequence[str] | None, recommended_persona: str | None) -> int:
    if recommended_persona and recommended_persona in (target_personas or []):
        return 70
    return 60
