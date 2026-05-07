from __future__ import annotations

from app.tools.scoring_tools import calculate_confidence_score, calculate_overall_score


def test_overall_score_formula_and_clamping() -> None:
    assert calculate_overall_score(80, 60, 50, 70) == 68
    assert calculate_overall_score(120, 120, 120, 120) == 100
    assert calculate_overall_score(-20, -10, -5, -1) == 0


def test_empty_evidence_lowers_confidence() -> None:
    empty_score, _ = calculate_confidence_score({"evidence": [], "risks": []}, {"signals": []})
    sourced_score, _ = calculate_confidence_score(
        {
            "evidence": [
                {
                    "claim": "Developer tooling fit",
                    "evidence": "The company sells developer infrastructure.",
                    "source_url": "https://example.com/devtools",
                    "confidence": "medium",
                }
            ],
            "risks": [],
        },
        {"signals": []},
    )

    assert empty_score < sourced_score


def test_strong_evidence_improves_confidence() -> None:
    weak_score, _ = calculate_confidence_score(
        {
            "evidence": [
                {
                    "claim": "Possible fit",
                    "evidence": "Somewhat relevant.",
                    "confidence": "low",
                }
            ],
            "risks": [{"risk": "Insufficient evidence", "reason": "Thin sourcing"}],
        },
        {"signals": []},
    )
    strong_score, _ = calculate_confidence_score(
        {
            "evidence": [
                {
                    "claim": "Strong product fit",
                    "evidence": "The company targets engineering leaders.",
                    "source_url": "https://example.com/company",
                    "confidence": "high",
                },
                {
                    "claim": "Technical buyer alignment",
                    "evidence": "The site speaks to platform teams.",
                    "source_url": "https://example.com/platform",
                    "confidence": "medium",
                },
            ],
            "risks": [],
        },
        {
            "signals": [
                {
                    "type": "growth_signal",
                    "description": "Hiring for platform engineers",
                    "source_url": "https://example.com/jobs",
                    "confidence": "high",
                }
            ]
        },
    )

    assert strong_score > weak_score
    assert 0 <= weak_score <= 100
    assert 0 <= strong_score <= 100
