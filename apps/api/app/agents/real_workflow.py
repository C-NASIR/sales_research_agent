from __future__ import annotations

from pydantic import BaseModel

from app.agents.schemas import ICPProfile, TodoItem
from app.providers.structured_llm import generate_structured_output
from app.tools.outreach_tools import generate_outreach_draft
from app.tools.quality_review_tools import review_outreach_draft
from app.tools.scoring_tools import build_score_report

ICP_SYSTEM_PROMPT = """
You are generating an ideal customer profile for a sales research workflow.
Use only the campaign brief and uploaded account list.
Do not invent private facts, market share, funding, or technology usage.
Return a practical ICP profile that stays conservative and source-agnostic.
""".strip()


class StructuredICPProfile(ICPProfile):
    pass


def build_run_todos() -> list[dict]:
    todos = [
        TodoItem(id="todo_icp", title="Define ICP and rubric", status="pending"),
        TodoItem(id="todo_research", title="Research accounts from public sources", status="pending"),
        TodoItem(id="todo_signals", title="Detect timing signals from evidence", status="pending"),
        TodoItem(id="todo_scoring", title="Score accounts from grounded evidence", status="pending"),
        TodoItem(id="todo_outreach", title="Generate and review outreach drafts", status="pending"),
    ]
    return [todo.model_dump(mode="json") for todo in todos]


def real_icp_strategist(brief: dict, normalized_accounts: list[dict]) -> dict:
    sample_accounts = normalized_accounts[: min(10, len(normalized_accounts))]
    icp = generate_structured_output(
        StructuredICPProfile,
        system_prompt=ICP_SYSTEM_PROMPT,
        user_payload={
            "campaign_brief": brief,
            "sample_accounts": sample_accounts,
            "account_count": len(normalized_accounts),
        },
        fallback_builder=lambda: _heuristic_icp_profile(brief, sample_accounts),
    )
    return icp.model_dump(mode="json")


def score_account(account: dict, brief: dict, research_report: dict, signal_report: dict, icp: dict) -> dict:
    return build_score_report(account, brief, icp, research_report, signal_report)


def generate_reviewed_outreach(
    brief: dict,
    account: dict,
    research_report: dict,
    signal_report: dict,
    score_report: dict,
) -> tuple[dict, dict]:
    draft = generate_outreach_draft(account, brief, research_report, signal_report, score_report)
    review = review_outreach_draft(draft, research_report, signal_report)
    return draft, review


def _heuristic_icp_profile(brief: dict, normalized_accounts: list[dict]) -> StructuredICPProfile:
    personas = [item.strip() for item in brief.get("target_persona", "").split(",") if item.strip()]
    domain_hints = [item["domain"] for item in normalized_accounts[:3] if item.get("domain")]
    target_company_criteria = [
        brief.get("ideal_customer_profile", "B2B teams with meaningful operational complexity."),
        "Accounts with a public product surface and evidence of active software delivery.",
    ]
    if domain_hints:
        target_company_criteria.append(f"Representative uploaded domains include: {', '.join(domain_hints)}.")
    return StructuredICPProfile(
        target_company_criteria=target_company_criteria,
        target_personas=personas or ["VP Engineering"],
        positive_signals=[
            "Public product or pricing information exists",
            "Engineering, careers, or workflow evidence appears on public pages",
            "Evidence suggests operational complexity relevant to the campaign pain statement",
        ],
        negative_signals=[
            "Public evidence is too thin to support confident outreach",
            "Company positioning appears unrelated to the campaign problem area",
            "No clear operating persona can be supported from public evidence",
        ],
        scoring_rubric={
            "fit": "How closely the public evidence matches the campaign ICP.",
            "timing": "Whether public signals indicate active change, growth, or urgency.",
            "confidence": "How well the account is supported by source-backed evidence.",
            "persona": "How clearly the campaign persona maps to the observed company context.",
        },
    )
