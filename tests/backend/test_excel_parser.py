import uuid
from datetime import datetime

import pytest

from app.models.campaign import BiddingStrategy, CampaignStatus
from app.models.keyword import MatchType
from app.schemas.pipeline import (
    AdGroupResponse,
    AdResponse,
    CampaignGenerateResponse,
    KeywordResponse,
)
from app.services.excel_export import generate_workbook
from app.services.excel_parser import ExcelParseError, parse_workbook


@pytest.fixture(autouse=True)
def setup_db():
    """Override the async DB fixture -- these tests don't need a database."""
    yield


AG_ID = uuid.uuid4()
CAMPAIGN_ID = uuid.uuid4()


def _make_campaign(**overrides) -> CampaignGenerateResponse:
    defaults = {
        "id": CAMPAIGN_ID,
        "name": "Test Campaign",
        "landing_page_url": "https://example.com",
        "status": CampaignStatus.REVIEW,
        "bidding_strategy": BiddingStrategy.MANUAL_CPC,
        "daily_budget": 50.0,
        "match_types": ["phrase", "exact"],
        "negative_keywords": ["free", "cheap"],
        "bid_value": 2.50,
        "location_targeting": "US, UK",
        "created_at": datetime(2026, 1, 1, 0, 0, 0),
        "updated_at": datetime(2026, 1, 2, 0, 0, 0),
        "ad_groups": [
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
                    KeywordResponse(
                        id=uuid.uuid4(),
                        text="best widgets",
                        match_type=MatchType.EXACT,
                        bid=None,
                        ad_group_id=AG_ID,
                    ),
                ],
                ads=[
                    AdResponse(
                        id=uuid.uuid4(),
                        final_url="https://example.com",
                        headlines=[
                            {"text": "Buy Widgets", "position": 1, "trigger": "urgency"},
                            {"text": "Best Price", "position": 2, "trigger": "value proposition"},
                        ],
                        descriptions=[
                            {"text": "Shop now", "trigger": "call to action"},
                            {"text": "Free shipping"},
                        ],
                        path1="widgets",
                        path2="buy",
                        ad_group_id=AG_ID,
                    ),
                ],
            ),
        ],
    }
    defaults.update(overrides)
    return CampaignGenerateResponse(**defaults)


def _roundtrip(**overrides):
    """Generate workbook bytes and parse them back."""
    campaign = _make_campaign(**overrides)
    wb_bytes = generate_workbook(campaign)
    return parse_workbook(wb_bytes)


def test_roundtrip_campaign_name():
    result = _roundtrip()
    assert result.campaign.name == "Test Campaign"


def test_roundtrip_landing_page_url():
    result = _roundtrip()
    assert result.campaign.landing_page_url == "https://example.com"


def test_roundtrip_bidding_strategy():
    result = _roundtrip()
    assert result.campaign.bidding_strategy == "manual_cpc"


def test_roundtrip_daily_budget():
    result = _roundtrip()
    assert result.campaign.daily_budget == 50.0


def test_roundtrip_match_types():
    result = _roundtrip()
    assert result.campaign.match_types == ["phrase", "exact"]


def test_roundtrip_negative_keywords():
    result = _roundtrip()
    assert result.campaign.negative_keywords == ["free", "cheap"]


def test_roundtrip_bid_value():
    result = _roundtrip()
    assert result.campaign.bid_value == 2.50


def test_roundtrip_location_targeting():
    result = _roundtrip()
    assert result.campaign.location_targeting == "US, UK"


def test_roundtrip_keywords():
    result = _roundtrip()
    assert len(result.keywords) == 2
    assert result.keywords[0].ad_group == "Ad Group 1"
    assert result.keywords[0].text == "buy widgets"
    assert result.keywords[0].match_type == "phrase"
    assert result.keywords[0].bid == 1.50
    assert result.keywords[1].text == "best widgets"
    assert result.keywords[1].match_type == "exact"


def test_roundtrip_ads_count():
    result = _roundtrip()
    assert len(result.ads) == 1


def test_roundtrip_headlines_and_pins():
    result = _roundtrip()
    ad = result.ads[0]
    assert len(ad.headlines) == 2
    assert ad.headlines[0].text == "Buy Widgets"
    assert ad.headlines[0].pin_position == 1
    assert ad.headlines[1].text == "Best Price"
    assert ad.headlines[1].pin_position == 2


def test_roundtrip_descriptions():
    result = _roundtrip()
    ad = result.ads[0]
    assert len(ad.descriptions) == 2
    assert ad.descriptions[0].text == "Shop now"
    assert ad.descriptions[1].text == "Free shipping"


def test_roundtrip_paths():
    result = _roundtrip()
    ad = result.ads[0]
    assert ad.path1 == "widgets"
    assert ad.path2 == "buy"


def test_roundtrip_final_url():
    result = _roundtrip()
    ad = result.ads[0]
    assert ad.final_url == "https://example.com"


def test_invalid_file_raises():
    with pytest.raises(ExcelParseError, match="Cannot open file"):
        parse_workbook(b"not an excel file")


def test_missing_sheets_raises():
    from openpyxl import Workbook
    from io import BytesIO

    wb = Workbook()
    wb.active.title = "Summary"
    buf = BytesIO()
    wb.save(buf)
    with pytest.raises(ExcelParseError, match="Missing required sheets"):
        parse_workbook(buf.getvalue())


def test_empty_campaign_roundtrip():
    result = _roundtrip(ad_groups=[])
    assert len(result.keywords) == 0
    assert len(result.ads) == 0
