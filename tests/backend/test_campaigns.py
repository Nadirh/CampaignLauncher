import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.ad_group import AdGroup
from app.models.campaign import Campaign, CampaignStatus
from app.models.keyword import Keyword, MatchType

REQUIRED_SETTINGS = {
    "bidding_strategy": "target_cpa",
    "daily_budget": 50.0,
    "match_types": ["phrase", "exact"],
    "bid_value": 2.50,
    "location_targeting": "US",
}


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
        **REQUIRED_SETTINGS,
    }
    response = await client.post("/api/campaigns", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Campaign"
    assert data["landing_page_url"] == "https://example.com/"
    assert data["status"] == "draft"
    assert data["bidding_strategy"] == "target_cpa"
    assert "id" in data


async def test_create_campaign_with_settings(client: AsyncClient) -> None:
    payload = {
        "name": "Settings Campaign",
        "landing_page_url": "https://example.com",
        "bidding_strategy": "maximize_clicks",
        "daily_budget": 100.0,
        "match_types": ["phrase", "exact"],
        "negative_keywords": ["free", "cheap"],
        "bid_value": 2.50,
        "location_targeting": "US, UK",
    }
    response = await client.post("/api/campaigns", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["bidding_strategy"] == "maximize_clicks"
    assert data["daily_budget"] == 100.0
    assert data["match_types"] == ["phrase", "exact"]
    assert data["negative_keywords"] == ["free", "cheap"]
    assert data["bid_value"] == 2.50
    assert data["location_targeting"] == "US, UK"


async def test_update_campaign_settings(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Update Settings", "landing_page_url": "https://example.com", **REQUIRED_SETTINGS},
    )
    campaign_id = create_resp.json()["id"]
    response = await client.put(
        f"/api/campaigns/{campaign_id}",
        json={
            "match_types": ["broad"],
            "negative_keywords": ["discount"],
            "bid_value": 5.00,
            "location_targeting": "CA",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["match_types"] == ["broad"]
    assert data["negative_keywords"] == ["discount"]
    assert data["bid_value"] == 5.00
    assert data["location_targeting"] == "CA"


async def test_list_campaigns_after_create(client: AsyncClient) -> None:
    payload = {
        "name": "Campaign A",
        "landing_page_url": "https://example.com",
        **REQUIRED_SETTINGS,
    }
    await client.post("/api/campaigns", json=payload)
    response = await client.get("/api/campaigns")
    data = response.json()
    assert data["total"] == 1
    assert data["campaigns"][0]["name"] == "Campaign A"


async def test_get_campaign(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Get Me", "landing_page_url": "https://example.com", **REQUIRED_SETTINGS},
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
        json={"name": "Original", "landing_page_url": "https://example.com", **REQUIRED_SETTINGS},
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
        json={"name": "Delete Me", "landing_page_url": "https://example.com", **REQUIRED_SETTINGS},
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


async def test_get_campaign_with_nested_ad_groups(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    campaign = Campaign(
        name="Nested Test",
        landing_page_url="https://example.com",
        status=CampaignStatus.REVIEW,
    )
    db_session.add(campaign)
    await db_session.flush()

    ad_group = AdGroup(name="Ad Group 1", campaign_id=campaign.id)
    db_session.add(ad_group)
    await db_session.flush()

    keyword = Keyword(text="test keyword", match_type=MatchType.PHRASE, ad_group_id=ad_group.id)
    ad = Ad(
        final_url="https://example.com",
        headlines=[{"text": "Headline 1"}],
        descriptions=[{"text": "Desc 1"}],
        ad_group_id=ad_group.id,
    )
    db_session.add_all([keyword, ad])
    await db_session.commit()

    response = await client.get(f"/api/campaigns/{campaign.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nested Test"
    assert len(data["ad_groups"]) == 1
    assert data["ad_groups"][0]["name"] == "Ad Group 1"
    assert len(data["ad_groups"][0]["keywords"]) == 1
    assert data["ad_groups"][0]["keywords"][0]["text"] == "test keyword"
    assert len(data["ad_groups"][0]["ads"]) == 1


async def test_approve_campaign_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    campaign = Campaign(
        name="Approve Me",
        landing_page_url="https://example.com",
        status=CampaignStatus.REVIEW,
    )
    db_session.add(campaign)
    await db_session.commit()

    response = await client.post(f"/api/campaigns/{campaign.id}/approve")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


async def test_approve_campaign_wrong_status(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    campaign = Campaign(
        name="Draft Campaign",
        landing_page_url="https://example.com",
        status=CampaignStatus.DRAFT,
    )
    db_session.add(campaign)
    await db_session.commit()

    response = await client.post(f"/api/campaigns/{campaign.id}/approve")
    assert response.status_code == 409


async def test_approve_campaign_not_found(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.post(f"/api/campaigns/{fake_id}/approve")
    assert response.status_code == 404


async def test_reject_campaign_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    campaign = Campaign(
        name="Reject Me",
        landing_page_url="https://example.com",
        status=CampaignStatus.REVIEW,
    )
    db_session.add(campaign)
    await db_session.commit()

    response = await client.post(f"/api/campaigns/{campaign.id}/reject")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "draft"


async def test_reject_campaign_wrong_status(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    campaign = Campaign(
        name="Approved Campaign",
        landing_page_url="https://example.com",
        status=CampaignStatus.APPROVED,
    )
    db_session.add(campaign)
    await db_session.commit()

    response = await client.post(f"/api/campaigns/{campaign.id}/reject")
    assert response.status_code == 409


async def test_reject_campaign_not_found(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.post(f"/api/campaigns/{fake_id}/reject")
    assert response.status_code == 404
