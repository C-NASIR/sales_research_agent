from __future__ import annotations


def test_campaign_create_list_and_get(client, campaign_payload) -> None:
    create_response = client.post("/campaigns", json=campaign_payload)

    assert create_response.status_code == 201
    created = create_response.json()
    campaign_id = created["id"]
    assert created["status"] == "draft"

    list_response = client.get("/campaigns")
    assert list_response.status_code == 200
    campaigns = list_response.json()["campaigns"]
    assert len(campaigns) == 1
    assert campaigns[0]["id"] == campaign_id

    get_response = client.get(f"/campaigns/{campaign_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == campaign_payload["name"]


def test_missing_campaign_returns_404(client) -> None:
    response = client.get("/campaigns/campaign_missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Campaign not found."}
