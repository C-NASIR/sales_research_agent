from __future__ import annotations

from collections.abc import Sequence


def sort_accounts_by_overall_score(accounts: Sequence[dict]) -> list[dict]:
    return sorted(
        accounts,
        key=lambda item: (item.get("overall_score") is None, -(item.get("overall_score") or 0)),
    )
