from __future__ import annotations

from pathlib import Path


def test_review_and_export_flow(client, campaign_payload) -> None:
    campaign_id = client.post("/campaigns", json=campaign_payload).json()["id"]
    upload_response = client.post(
        f"/campaigns/{campaign_id}/upload",
        files={
            "file": (
                "accounts.csv",
                (
                    "company_name,domain\n"
                    "Sentry,sentry.io\n"
                    "Vercel,vercel.com\n"
                ).encode("utf-8"),
                "text/csv",
            )
        },
    )
    assert upload_response.status_code == 200

    run_response = client.post(f"/campaigns/{campaign_id}/runs")
    assert run_response.status_code == 200

    results_response = client.get(f"/campaigns/{campaign_id}/results")
    assert results_response.status_code == 200
    account_id = results_response.json()["accounts"][0]["account_id"]

    no_approved_export = client.post(
        f"/campaigns/{campaign_id}/exports",
        json={"include_review_statuses": ["approved"]},
    )
    assert no_approved_export.status_code == 400
    assert no_approved_export.json()["detail"] == "No accounts are available for export."

    invalid_review = client.patch(
        f"/campaigns/{campaign_id}/accounts/{account_id}/review",
        json={"review_status": "bad_status"},
    )
    assert invalid_review.status_code == 400
    assert invalid_review.json()["detail"] == "review_status: Value error, Invalid review status."

    review_response = client.patch(
        f"/campaigns/{campaign_id}/accounts/{account_id}/review",
        json={"review_status": "approved"},
    )
    assert review_response.status_code == 200
    assert review_response.json()["review_status"] == "approved"

    draft_response = client.patch(
        f"/campaigns/{campaign_id}/accounts/{account_id}/draft",
        json={
            "subject": "Shorter review cycles",
            "body": "Hi team,\n\nWe help engineering leaders tighten review quality.\n",
        },
    )
    assert draft_response.status_code == 200
    assert draft_response.json()["subject"] == "Shorter review cycles"

    export_response = client.post(
        f"/campaigns/{campaign_id}/exports",
        json={"include_review_statuses": ["approved"]},
    )
    assert export_response.status_code == 200
    exports = export_response.json()["exports"]
    assert len(exports) == 3
    for export_file in exports:
        assert Path(export_file["file_path"]).is_file()
