import uuid
from datetime import datetime
from io import BytesIO

import pytest
from openpyxl import Workbook

from app.models.campaign import BiddingStrategy, CampaignStatus
from app.models.keyword import MatchType
from app.schemas.pipeline import (
    AdGroupResponse,
    AdResponse,
    CampaignGenerateResponse,
    KeywordResponse,
)
from app.services.excel_export import generate_workbook


AG_ID = uuid.uuid4()
CAMPAIGN_ID = uuid.uuid4()

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _make_valid_xlsx() -> bytes:
    campaign = CampaignGenerateResponse(
        id=CAMPAIGN_ID,
        name="Test Campaign",
        landing_page_url="https://example.com",
        status=CampaignStatus.REVIEW,
        bidding_strategy=BiddingStrategy.MANUAL_CPC,
        daily_budget=50.0,
        match_types=["phrase"],
        negative_keywords=["free"],
        bid_value=2.50,
        location_targeting="US",
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
        ad_groups=[
            AdGroupResponse(
                id=AG_ID,
                name="Ad Group 1",
                campaign_id=CAMPAIGN_ID,
                keywords=[
                    KeywordResponse(
                        id=uuid.uuid4(),
                        text="buy widgets",
                        match_type=MatchType.PHRASE,
                        bid=1.50,
                        ad_group_id=AG_ID,
                    ),
                ],
                ads=[
                    AdResponse(
                        id=uuid.uuid4(),
                        final_url="https://example.com",
                        headlines=[{"text": "Buy Widgets", "position": 1}],
                        descriptions=[{"text": "Shop now"}],
                        path1="widgets",
                        path2=None,
                        ad_group_id=AG_ID,
                    ),
                ],
            ),
        ],
    )
    return generate_workbook(campaign)


async def _create_campaign(client) -> str:
    resp = await client.post("/api/campaigns", json={
        "name": "Test Campaign",
        "landing_page_url": "https://example.com",
        "bidding_strategy": "manual_cpc",
        "daily_budget": 50.0,
        "match_types": ["phrase"],
        "bid_value": 2.50,
        "location_targeting": "US",
    })
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_generate_ads_script_success(client):
    campaign_id = await _create_campaign(client)
    xlsx_bytes = _make_valid_xlsx()

    resp = await client.post(
        f"/api/campaigns/{campaign_id}/ads-script",
        files={"file": ("campaign.xlsx", BytesIO(xlsx_bytes), XLSX_CONTENT_TYPE)},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "script" in data
    assert data["campaign_name"] == "Test Campaign"
    assert data["ad_group_count"] == 1
    assert data["keyword_count"] == 1
    assert data["ad_count"] == 1
    assert "Test Campaign" in data["script"]
    assert "PAUSED" in data["script"]


@pytest.mark.asyncio
async def test_campaign_not_found(client):
    fake_id = uuid.uuid4()
    xlsx_bytes = _make_valid_xlsx()

    resp = await client.post(
        f"/api/campaigns/{fake_id}/ads-script",
        files={"file": ("campaign.xlsx", BytesIO(xlsx_bytes), XLSX_CONTENT_TYPE)},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_invalid_file_type(client):
    campaign_id = await _create_campaign(client)

    resp = await client.post(
        f"/api/campaigns/{campaign_id}/ads-script",
        files={"file": ("data.csv", BytesIO(b"a,b,c"), "text/csv")},
    )
    assert resp.status_code == 400
    assert "xlsx" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_malformed_excel(client):
    campaign_id = await _create_campaign(client)

    # Valid xlsx but missing required sheets
    wb = Workbook()
    wb.active.title = "WrongSheet"
    buf = BytesIO()
    wb.save(buf)

    resp = await client.post(
        f"/api/campaigns/{campaign_id}/ads-script",
        files={"file": ("bad.xlsx", BytesIO(buf.getvalue()), XLSX_CONTENT_TYPE)},
    )
    assert resp.status_code == 422
    assert "Missing required sheets" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_xlsx_extension_accepted_without_content_type(client):
    campaign_id = await _create_campaign(client)
    xlsx_bytes = _make_valid_xlsx()

    resp = await client.post(
        f"/api/campaigns/{campaign_id}/ads-script",
        files={"file": ("campaign.xlsx", BytesIO(xlsx_bytes), "application/octet-stream")},
    )
    assert resp.status_code == 200
