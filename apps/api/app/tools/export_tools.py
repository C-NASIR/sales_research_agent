from __future__ import annotations

import csv
import json
from collections.abc import Sequence
from pathlib import Path


PROSPECT_CSV_COLUMNS = [
    "company_name",
    "domain",
    "overall_score",
    "fit_score",
    "timing_score",
    "confidence_score",
    "persona_score",
    "recommended_persona",
    "sales_angle",
    "review_status",
    "research_status",
    "draft_quality_status",
    "email_subject",
    "email_body",
    "personalization_source",
    "personalization_source_url",
    "evidence_summary",
    "risk_summary",
]


def sort_accounts_by_overall_score(accounts: Sequence[dict]) -> list[dict]:
    return sorted(
        accounts,
        key=lambda item: (item.get("overall_score") is None, -(item.get("overall_score") or 0)),
    )


def build_prospects_csv(rows: list[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PROSPECT_CSV_COLUMNS)
        writer.writeheader()
        for row in sort_accounts_by_overall_score(_flatten_export_rows(rows)):
            writer.writerow({column: row.get(column, "") for column in PROSPECT_CSV_COLUMNS})
    return output_path


def build_campaign_report_markdown(campaign: dict, rows: list[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {campaign['name']}",
        "",
        "## Campaign brief",
        f"- Product description: {campaign.get('product_description') or ''}",
        f"- Ideal customer profile: {campaign.get('ideal_customer_profile') or ''}",
        f"- Pain statement: {campaign.get('pain_statement') or ''}",
        f"- Target persona: {campaign.get('target_persona') or ''}",
        f"- Tone: {campaign.get('tone') or ''}",
        "",
        "## Export summary",
        f"- Exported at: {campaign.get('exported_at') or ''}",
        f"- Included review statuses: {', '.join(campaign.get('include_review_statuses') or [])}",
        f"- Exported accounts: {len(rows)}",
        "",
        "## Exported accounts",
        "",
    ]
    for row in sort_accounts_by_overall_score(_flatten_export_rows(rows)):
        lines.extend(
            [
                f"### {row['company_name']} ({row['domain']})",
                f"- Overall score: {_display_value(row['overall_score'])}",
                f"- Fit / timing / confidence / persona: {_display_value(row['fit_score'])} / {_display_value(row['timing_score'])} / {_display_value(row['confidence_score'])} / {_display_value(row['persona_score'])}",
                f"- Recommended persona: {row['recommended_persona'] or 'Missing'}",
                f"- Sales angle: {row['sales_angle'] or 'Missing'}",
                f"- Evidence summary: {row['evidence_summary'] or 'Missing'}",
                f"- Risk summary: {row['risk_summary'] or 'Missing'}",
                "- Outreach draft:",
                "",
                f"Subject: {row['email_subject'] or 'Missing'}",
                "",
                row["email_body"] or "Missing",
                "",
            ]
        )

    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return output_path


def build_archive_json(campaign: dict, rows: list[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "campaign": {
            "id": campaign.get("id"),
            "name": campaign.get("name"),
            "product_description": campaign.get("product_description"),
            "ideal_customer_profile": campaign.get("ideal_customer_profile"),
            "pain_statement": campaign.get("pain_statement"),
            "target_persona": campaign.get("target_persona"),
            "tone": campaign.get("tone"),
            "status": campaign.get("status"),
        },
        "exported_at": campaign.get("exported_at"),
        "include_review_statuses": campaign.get("include_review_statuses") or [],
        "accounts": rows,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def _flatten_export_rows(rows: list[dict]) -> list[dict]:
    flattened: list[dict] = []
    for row in rows:
        account = row.get("account") or {}
        score_report = row.get("score_report") or {}
        research_report = row.get("research_report") or {}
        outreach_draft = row.get("outreach_draft") or {}

        flattened.append(
            {
                "company_name": account.get("company_name") or "",
                "domain": account.get("domain") or "",
                "overall_score": score_report.get("overall_score"),
                "fit_score": score_report.get("fit_score"),
                "timing_score": score_report.get("timing_score"),
                "confidence_score": score_report.get("confidence_score"),
                "persona_score": score_report.get("persona_score"),
                "recommended_persona": score_report.get("recommended_persona") or "",
                "sales_angle": score_report.get("sales_angle") or outreach_draft.get("sales_angle") or "",
                "review_status": account.get("review_status") or "",
                "research_status": account.get("research_status") or "",
                "draft_quality_status": (row.get("quality_review") or {}).get("quality_status")
                or outreach_draft.get("quality_status")
                or "",
                "email_subject": outreach_draft.get("subject") or "",
                "email_body": outreach_draft.get("body") or "",
                "personalization_source": outreach_draft.get("personalization_source") or "",
                "personalization_source_url": outreach_draft.get("personalization_source_url") or "",
                "evidence_summary": _summarize_evidence(research_report),
                "risk_summary": _summarize_risks(research_report, outreach_draft),
            }
        )
    return flattened


def _summarize_evidence(research_report: dict) -> str:
    evidence_items = research_report.get("evidence") or []
    snippets = []
    for item in evidence_items[:3]:
        claim = item.get("claim") or ""
        evidence = item.get("evidence") or ""
        snippet = ": ".join(part for part in [claim, evidence] if part)
        if snippet:
            snippets.append(snippet)
    return " | ".join(snippets)


def _summarize_risks(research_report: dict, outreach_draft: dict) -> str:
    snippets = []
    for item in research_report.get("risks") or []:
        risk = item.get("risk") or ""
        reason = item.get("reason") or ""
        snippet = ": ".join(part for part in [risk, reason] if part)
        if snippet:
            snippets.append(snippet)
    for note in outreach_draft.get("risk_notes") or []:
        if note:
            snippets.append(note)
    return " | ".join(snippets)


def _display_value(value: object) -> str:
    return "Missing" if value is None or value == "" else str(value)
