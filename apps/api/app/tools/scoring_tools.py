from __future__ import annotations


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
