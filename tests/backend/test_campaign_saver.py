import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.ad_group import AdGroup
from app.models.campaign import Campaign, CampaignStatus
from app.models.keyword import Keyword, MatchType
from app.schemas.pipeline import (
    AdGroupData,
    CampaignStructure,
    DescriptionData,
    HeadlineData,
    KeywordData,
)
from app.services.campaign_saver import save_campaign_structure


def _make_structure() -> CampaignStructure:
    return CampaignStructure(
        ad_groups=[
            AdGroupData(
                name="Project Management",
                keywords=[
                    KeywordData(text="project management tool", match_type=MatchType.PHRASE),
                    KeywordData(text="project management tool", match_type=MatchType.EXACT),
                    KeywordData(text="task tracker", match_type=MatchType.PHRASE),
                ],
                headlines=[
                    HeadlineData(text="Ship Projects Faster", position=1),
                    HeadlineData(text="All-in-One PM Tool", position=2),
                ],
                descriptions=[
                    DescriptionData(text="Manage projects with ease. Real-time collaboration for teams."),
                ],
            ),
            AdGroupData(
                name="Team Collaboration",
                keywords=[
                    KeywordData(text="team collaboration software", match_type=MatchType.PHRASE),
                ],
                headlines=[
                    HeadlineData(text="Collaborate in Real Time", position=1),
                ],
                descriptions=[
                    DescriptionData(text="Work together seamlessly with real-time features."),
                ],
            ),
        ]
    )


async def _create_campaign(db: AsyncSession) -> Campaign:
    campaign = Campaign(
        name="Test Campaign",
        landing_page_url="https://example.com",
        status=CampaignStatus.DRAFT,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def test_creates_ad_groups(db_session: AsyncSession) -> None:
    campaign = await _create_campaign(db_session)
    structure = _make_structure()

    await save_campaign_structure(campaign, structure, db_session)

    result = await db_session.execute(
        select(AdGroup).where(AdGroup.campaign_id == campaign.id)
    )
    ad_groups = list(result.scalars().all())
    assert len(ad_groups) == 2
    names = {ag.name for ag in ad_groups}
    assert "Project Management" in names
    assert "Team Collaboration" in names


async def test_creates_keywords(db_session: AsyncSession) -> None:
    campaign = await _create_campaign(db_session)
    structure = _make_structure()

    await save_campaign_structure(campaign, structure, db_session)

    result = await db_session.execute(select(Keyword))
    keywords = list(result.scalars().all())
    assert len(keywords) == 4
    texts = [kw.text for kw in keywords]
    assert "project management tool" in texts
    assert "task tracker" in texts


async def test_keyword_match_types(db_session: AsyncSession) -> None:
    campaign = await _create_campaign(db_session)
    structure = _make_structure()

    await save_campaign_structure(campaign, structure, db_session)

    result = await db_session.execute(
        select(Keyword).where(Keyword.text == "project management tool")
    )
    keywords = list(result.scalars().all())
    match_types = {kw.match_type for kw in keywords}
    assert MatchType.PHRASE in match_types
    assert MatchType.EXACT in match_types


async def test_creates_ads(db_session: AsyncSession) -> None:
    campaign = await _create_campaign(db_session)
    structure = _make_structure()

    await save_campaign_structure(campaign, structure, db_session)

    result = await db_session.execute(select(Ad))
    ads = list(result.scalars().all())
    assert len(ads) == 2
    assert ads[0].final_url == "https://example.com"
    assert len(ads[0].headlines) >= 1
    assert len(ads[0].descriptions) >= 1


async def test_sets_campaign_status_to_review(db_session: AsyncSession) -> None:
    campaign = await _create_campaign(db_session)
    structure = _make_structure()

    result = await save_campaign_structure(campaign, structure, db_session)

    assert result.status == CampaignStatus.REVIEW


async def test_empty_structure(db_session: AsyncSession) -> None:
    campaign = await _create_campaign(db_session)
    structure = CampaignStructure(ad_groups=[])

    result = await save_campaign_structure(campaign, structure, db_session)

    assert result.status == CampaignStatus.REVIEW
    ad_groups_result = await db_session.execute(
        select(AdGroup).where(AdGroup.campaign_id == campaign.id)
    )
    assert len(list(ad_groups_result.scalars().all())) == 0
