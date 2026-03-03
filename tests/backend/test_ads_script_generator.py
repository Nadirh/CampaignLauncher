import pytest

from app.schemas.ads_script import (
    ParsedAd,
    ParsedCampaign,
    ParsedDescription,
    ParsedHeadline,
    ParsedKeyword,
    ParsedWorkbook,
)
from app.services.ads_script_generator import (
    _escape_js,
    _format_bidding_strategy,
    _format_keyword,
    _safe_var_name,
    generate_script,
)


@pytest.fixture(autouse=True)
def setup_db():
    """Override the async DB fixture -- these tests don't need a database."""
    yield


def _make_workbook(**overrides) -> ParsedWorkbook:
    defaults = {
        "campaign": ParsedCampaign(
            name="Test Campaign",
            landing_page_url="https://example.com",
            bidding_strategy="manual_cpc",
            daily_budget=50.0,
            match_types=["phrase", "exact"],
            negative_keywords=["free", "cheap"],
            bid_value=2.50,
            location_targeting="US, UK",
        ),
        "keywords": [
            ParsedKeyword(ad_group="Ad Group 1", text="buy widgets", match_type="phrase", bid=1.50),
            ParsedKeyword(ad_group="Ad Group 1", text="best widgets", match_type="exact", bid=None),
            ParsedKeyword(ad_group="Ad Group 2", text="widget deals", match_type="broad", bid=None),
        ],
        "ads": [
            ParsedAd(
                ad_group="Ad Group 1",
                ad_number=1,
                headlines=[
                    ParsedHeadline(text="Buy Widgets", pin_position=1),
                    ParsedHeadline(text="Best Price", pin_position=2),
                    ParsedHeadline(text="Shop Now", pin_position=None),
                ],
                descriptions=[
                    ParsedDescription(text="Shop now for great deals"),
                    ParsedDescription(text="Free shipping available"),
                ],
                final_url="https://example.com",
                path1="widgets",
                path2="buy",
            ),
        ],
    }
    defaults.update(overrides)
    return ParsedWorkbook(**defaults)


def test_script_contains_campaign_name():
    script = generate_script(_make_workbook())
    assert "Test Campaign" in script


def test_script_contains_paused_status():
    script = generate_script(_make_workbook())
    assert '"PAUSED"' in script


def test_script_contains_budget():
    script = generate_script(_make_workbook())
    assert ".withBudget(50.0)" in script


def test_script_contains_bidding_strategy():
    script = generate_script(_make_workbook())
    assert "MANUAL_CPC" in script


def test_script_contains_ad_groups():
    script = generate_script(_make_workbook())
    assert "Ad Group 1" in script
    assert "Ad Group 2" in script


def test_script_contains_phrase_keyword():
    script = generate_script(_make_workbook())
    assert '\\"buy widgets\\"' in script


def test_script_contains_exact_keyword():
    script = generate_script(_make_workbook())
    assert "[best widgets]" in script


def test_script_contains_broad_keyword():
    script = generate_script(_make_workbook())
    assert '.withText("widget deals")' in script


def test_script_contains_headlines():
    script = generate_script(_make_workbook())
    assert "Buy Widgets" in script
    assert "Best Price" in script
    assert "Shop Now" in script


def test_script_contains_pin_positions():
    script = generate_script(_make_workbook())
    assert "HEADLINE_1" in script
    assert "HEADLINE_2" in script


def test_script_contains_descriptions():
    script = generate_script(_make_workbook())
    assert "Shop now for great deals" in script
    assert "Free shipping available" in script


def test_script_contains_negative_keywords():
    script = generate_script(_make_workbook())
    assert 'createNegativeKeyword("free")' in script
    assert 'createNegativeKeyword("cheap")' in script


def test_script_contains_location_targeting():
    script = generate_script(_make_workbook())
    assert "addLocation(2840)" in script  # US
    assert "addLocation(2826)" in script  # UK


def test_script_contains_duplicate_check():
    script = generate_script(_make_workbook())
    assert "already exists" in script
    assert "Aborting" in script


def test_script_contains_paths():
    script = generate_script(_make_workbook())
    assert '.withPath1("widgets")' in script
    assert '.withPath2("buy")' in script


def test_script_contains_final_url():
    script = generate_script(_make_workbook())
    assert '.withFinalUrl("https://example.com")' in script


def test_script_contains_keyword_bid():
    script = generate_script(_make_workbook())
    assert ".withCpc(1.5)" in script


def test_script_unknown_location():
    wb = _make_workbook()
    wb.campaign.location_targeting = "JP"
    script = generate_script(wb)
    assert "Unknown location: JP" in script


def test_script_no_negatives():
    wb = _make_workbook()
    wb.campaign.negative_keywords = None
    script = generate_script(wb)
    assert "createNegativeKeyword" not in script


def test_script_no_location():
    wb = _make_workbook()
    wb.campaign.location_targeting = None
    script = generate_script(wb)
    assert "addLocation" not in script
    assert "Unknown location" not in script


# Helper function tests

def test_escape_js_quotes():
    assert _escape_js('He said "hello"') == 'He said \\"hello\\"'
    assert _escape_js("it's") == "it\\'s"


def test_format_keyword_exact():
    assert _format_keyword("widgets", "exact") == "[widgets]"


def test_format_keyword_phrase():
    assert _format_keyword("widgets", "phrase") == '\\"widgets\\"'


def test_format_keyword_broad():
    assert _format_keyword("widgets", "broad") == "widgets"


def test_safe_var_name():
    assert _safe_var_name("Ad Group 1", 0) == "AdGroup1_0"
    assert _safe_var_name("123", 1) == "adGroup123_1"


def test_format_bidding_strategy():
    assert _format_bidding_strategy("manual_cpc") == "MANUAL_CPC"
    assert _format_bidding_strategy("target_cpa") == "TARGET_CPA"
    assert _format_bidding_strategy("unknown") == "UNKNOWN"
