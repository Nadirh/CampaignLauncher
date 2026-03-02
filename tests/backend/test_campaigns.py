import uuid

from httpx import AsyncClient


async def test_list_campaigns_empty(client: AsyncClient) -> None:
    response = await client.get("/api/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert data["campaigns"] == []
    assert data["total"] == 0


async def test_create_campaign(client: AsyncClient) -> None:
    payload = {
        "name": "Test Campaign",
        "landing_page_url": "https://example.com",
    }
    response = await client.post("/api/campaigns", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Campaign"
    assert data["landing_page_url"] == "https://example.com/"
    assert data["status"] == "draft"
    assert data["bidding_strategy"] == "manual_cpc"
    assert "id" in data


async def test_list_campaigns_after_create(client: AsyncClient) -> None:
    payload = {
        "name": "Campaign A",
        "landing_page_url": "https://example.com",
    }
    await client.post("/api/campaigns", json=payload)
    response = await client.get("/api/campaigns")
    data = response.json()
    assert data["total"] == 1
    assert data["campaigns"][0]["name"] == "Campaign A"


async def test_get_campaign(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Get Me", "landing_page_url": "https://example.com"},
    )
    campaign_id = create_resp.json()["id"]
    response = await client.get(f"/api/campaigns/{campaign_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Me"


async def test_get_campaign_not_found(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/campaigns/{fake_id}")
    assert response.status_code == 404


async def test_update_campaign(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Original", "landing_page_url": "https://example.com"},
    )
    campaign_id = create_resp.json()["id"]
    response = await client.put(
        f"/api/campaigns/{campaign_id}",
        json={"name": "Updated", "status": "review"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["status"] == "review"


async def test_update_campaign_not_found(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.put(
        f"/api/campaigns/{fake_id}",
        json={"name": "Nope"},
    )
    assert response.status_code == 404


async def test_delete_campaign(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Delete Me", "landing_page_url": "https://example.com"},
    )
    campaign_id = create_resp.json()["id"]
    response = await client.delete(f"/api/campaigns/{campaign_id}")
    assert response.status_code == 204

    get_resp = await client.get(f"/api/campaigns/{campaign_id}")
    assert get_resp.status_code == 404


async def test_delete_campaign_not_found(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.delete(f"/api/campaigns/{fake_id}")
    assert response.status_code == 404
