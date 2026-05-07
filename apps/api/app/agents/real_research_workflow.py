from __future__ import annotations

from app.services.research_service import get_cached_research_context, run_real_account_research


def real_account_researcher(account: dict, icp: dict, brief: dict) -> dict:
    research_report, signal_report = run_real_account_research(account, brief, icp)
    _REAL_REPORT_CACHE[(account["company_name"], account["domain"])] = {
        "research_report": research_report,
        "signal_report": signal_report,
    }
    return research_report


def real_signal_detector(account: dict, research_report: dict, icp: dict, brief: dict) -> dict:
    cached = _REAL_REPORT_CACHE.get((account["company_name"], account["domain"]))
    if cached is not None:
        return cached["signal_report"]
    _, signal_report = run_real_account_research(account, brief, icp)
    return signal_report


def get_real_research_context(account: dict):
    return get_cached_research_context(account)


_REAL_REPORT_CACHE: dict[tuple[str, str], dict] = {}
