import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad
from app.models.ad_group import AdGroup
from app.models.campaign import Campaign, CampaignStatus
from app.models.keyword import Keyword, MatchType
from app.schemas.pipeline import CampaignStructure

logger = logging.getLogger(__name__)


class CampaignSaverError(Exception):
    pass


async def save_campaign_structure(
    campaign: Campaign,
    structure: CampaignStructure,
    db: AsyncSession,
) -> Campaign:
    """Save generated ad groups, keywords, and ads to the database.

    Sets campaign status to REVIEW on success. Uses a single commit for atomicity.
    """
    for ag_data in structure.ad_groups:
        ad_group = AdGroup(
            name=ag_data.name,
            campaign_id=campaign.id,
        )
        db.add(ad_group)
        await db.flush()

        for kw_data in ag_data.keywords:
            match_type = kw_data.match_type
            if isinstance(match_type, str):
                match_type = MatchType(match_type)

            keyword = Keyword(
                text=kw_data.text,
                match_type=match_type,
                ad_group_id=ad_group.id,
            )
            db.add(keyword)

        headlines = [{"text": h.text, "position": h.position} for h in ag_data.headlines]
        descriptions = [{"text": d.text} for d in ag_data.descriptions]

        ad = Ad(
            final_url=campaign.landing_page_url,
            headlines=headlines,
            descriptions=descriptions,
            ad_group_id=ad_group.id,
        )
        db.add(ad)

    campaign.status = CampaignStatus.REVIEW
    await db.commit()
    await db.refresh(campaign)

    logger.info(
        "Campaign structure saved",
        extra={
            "campaign_id": str(campaign.id),
            "ad_groups_created": len(structure.ad_groups),
            "status": campaign.status.value,
        },
    )

    return campaign
