from __future__ import annotations


def test_upload_sample_csv_creates_accounts_and_detects_duplicates(client, campaign_payload) -> None:
    campaign_id = client.post("/campaigns", json=campaign_payload).json()["id"]
    csv_bytes = (
        "company_name,domain\n"
        "Sentry,sentry.io\n"
        "PostHog,posthog.com\n"
        "Sentry Duplicate,https://sentry.io/pricing\n"
    ).encode("utf-8")

    response = client.post(
        f"/campaigns/{campaign_id}/upload",
        files={"file": ("accounts.csv", csv_bytes, "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["created_accounts"] == 2
    assert payload["duplicate_rows"] == 1
    assert payload["duplicates"][0]["domain"] == "sentry.io"

    accounts_response = client.get(f"/campaigns/{campaign_id}/accounts")
    assert accounts_response.status_code == 200
    assert len(accounts_response.json()["accounts"]) == 2


def test_upload_missing_required_columns_returns_400(client, campaign_payload) -> None:
    campaign_id = client.post("/campaigns", json=campaign_payload).json()["id"]

    response = client.post(
        f"/campaigns/{campaign_id}/upload",
        files={"file": ("accounts.csv", b"name,website\nAcme,acme.com\n", "text/csv")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing required columns: company_name, domain."
