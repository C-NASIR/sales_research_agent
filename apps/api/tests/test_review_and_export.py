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


def test_run_uses_low_confidence_fallback_when_search_fails(client_factory, campaign_payload) -> None:
    with client_factory({"STUB_SEARCH_BEHAVIOR": "error"}) as client:
        campaign_id = client.post("/campaigns", json=campaign_payload).json()["id"]
        upload_response = client.post(
            f"/campaigns/{campaign_id}/upload",
            files={
                "file": (
                    "accounts.csv",
                    "company_name,domain\nSentry,sentry.io\n".encode("utf-8"),
                    "text/csv",
                )
            },
        )
        assert upload_response.status_code == 200

        run_response = client.post(f"/campaigns/{campaign_id}/runs")
        assert run_response.status_code == 200

        latest_run = client.get(f"/campaigns/{campaign_id}/runs/latest")
        assert latest_run.status_code == 200
        assert latest_run.json()["status"] == "completed"

        results_response = client.get(f"/campaigns/{campaign_id}/results")
        account_id = results_response.json()["accounts"][0]["account_id"]
        account_detail = client.get(f"/campaigns/{campaign_id}/accounts/{account_id}")
        assert account_detail.status_code == 200
        research_report = account_detail.json()["research_report"]
        assert research_report["confidence"] == 20
        assert "inconclusive" in research_report["company_summary"].lower()


def test_fake_mode_is_rejected(client_factory, campaign_payload) -> None:
    with client_factory({"RESEARCH_MODE": "fake"}) as client:
        campaign_id = client.post("/campaigns", json=campaign_payload).json()["id"]
        upload_response = client.post(
            f"/campaigns/{campaign_id}/upload",
            files={
                "file": (
                    "accounts.csv",
                    "company_name,domain\nSentry,sentry.io\n".encode("utf-8"),
                    "text/csv",
                )
            },
        )
        assert upload_response.status_code == 200

        run_response = client.post(f"/campaigns/{campaign_id}/runs")
        assert run_response.status_code == 200

        latest_run = client.get(f"/campaigns/{campaign_id}/runs/latest")
        assert latest_run.status_code == 200
        assert latest_run.json()["status"] == "failed"
        assert "only supports 'real'" in (latest_run.json()["error_message"] or "")
