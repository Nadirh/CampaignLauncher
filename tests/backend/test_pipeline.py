import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient

from app.schemas.pipeline import (
    AdGroupData,
    CampaignStructure,
    DescriptionData,
    HeadlineData,
    KeywordData,
    PageContent,
)
from app.services.page_fetcher import PageFetchError
from app.services.claude_analyzer import ClaudeAnalyzerError


MOCK_PAGE_CONTENT = PageContent(
    url="https://example.com",
    title="Example",
    meta_description="Test",
    headings=["Main Heading"],
    raw_text="Some content",
)

MOCK_STRUCTURE = CampaignStructure(
    ad_groups=[
        AdGroupData(
            name="Test Ad Group",
            keywords=[
                KeywordData(text="test keyword", match_type="phrase"),
                KeywordData(text="test keyword", match_type="exact"),
            ],
            headlines=[
                HeadlineData(text="Test Headline One", position=1),
                HeadlineData(text="Another Headline", position=2),
            ],
            descriptions=[
                DescriptionData(text="This is a test description for the ad group."),
            ],
        )
    ]
)


def _patch_pipeline():
    """Return context managers that mock the pipeline services."""
    fetch_mock = patch(
        "app.services.pipeline.fetch_page",
        new_callable=AsyncMock,
        return_value=MOCK_PAGE_CONTENT,
    )
    analyze_mock = patch(
        "app.services.pipeline.analyze_page",
        new_callable=AsyncMock,
        return_value=MOCK_STRUCTURE,
    )
    return fetch_mock, analyze_mock


async def test_generate_success(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Pipeline Test", "landing_page_url": "https://example.com"},
    )
    campaign_id = create_resp.json()["id"]

    fetch_mock, analyze_mock = _patch_pipeline()
    with fetch_mock, analyze_mock:
        response = await client.post(f"/api/campaigns/{campaign_id}/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "review"
    assert len(data["ad_groups"]) == 1
    assert data["ad_groups"][0]["name"] == "Test Ad Group"
    assert len(data["ad_groups"][0]["keywords"]) == 2
    assert len(data["ad_groups"][0]["ads"]) == 1


async def test_generate_not_found(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.post(f"/api/campaigns/{fake_id}/generate")
    assert response.status_code == 404


async def test_generate_not_draft(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Not Draft", "landing_page_url": "https://example.com"},
    )
    campaign_id = create_resp.json()["id"]

    # Set status to review
    await client.put(
        f"/api/campaigns/{campaign_id}",
        json={"status": "review"},
    )

    fetch_mock, analyze_mock = _patch_pipeline()
    with fetch_mock, analyze_mock:
        response = await client.post(f"/api/campaigns/{campaign_id}/generate")

    assert response.status_code == 400
    assert "draft" in response.json()["detail"].lower()


async def test_generate_fetch_failure(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Fetch Fail", "landing_page_url": "https://example.com"},
    )
    campaign_id = create_resp.json()["id"]

    with (
        patch(
            "app.services.pipeline.fetch_page",
            new_callable=AsyncMock,
            side_effect=PageFetchError("Connection timeout"),
        ),
    ):
        response = await client.post(f"/api/campaigns/{campaign_id}/generate")

    assert response.status_code == 502
    assert "Connection timeout" in response.json()["detail"]


async def test_generate_claude_failure(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/campaigns",
        json={"name": "Claude Fail", "landing_page_url": "https://example.com"},
    )
    campaign_id = create_resp.json()["id"]

    with (
        patch(
            "app.services.pipeline.fetch_page",
            new_callable=AsyncMock,
            return_value=MOCK_PAGE_CONTENT,
        ),
        patch(
            "app.services.pipeline.analyze_page",
            new_callable=AsyncMock,
            side_effect=ClaudeAnalyzerError("Rate limited"),
        ),
    ):
        response = await client.post(f"/api/campaigns/{campaign_id}/generate")

    assert response.status_code == 502
    assert "Rate limited" in response.json()["detail"]
