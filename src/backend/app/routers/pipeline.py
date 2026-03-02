import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.ad_group import AdGroup
from app.models.campaign import Campaign
from app.schemas.pipeline import CampaignGenerateResponse
from app.services.pipeline import PipelineError, run_pipeline

router = APIRouter(prefix="/api/campaigns", tags=["pipeline"])


@router.post(
    "/{campaign_id}/generate",
    response_model=CampaignGenerateResponse,
)
async def generate_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CampaignGenerateResponse:
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        await run_pipeline(campaign, db)
    except PipelineError as exc:
        status_map = {
            "validation": 400,
            "fetch": 502,
            "analyze": 502,
            "save": 500,
        }
        status_code = status_map.get(exc.step, 500)
        raise HTTPException(status_code=status_code, detail=str(exc))

    # Reload with relationships for the response using a fresh query
    # (db.get caches the identity map entry and won't eagerly load new children)
    db.expire(campaign)
    stmt = (
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(
            selectinload(Campaign.ad_groups).selectinload(AdGroup.keywords),
            selectinload(Campaign.ad_groups).selectinload(AdGroup.ads),
        )
    )
    result_row = await db.execute(stmt)
    result = result_row.scalar_one()

    return CampaignGenerateResponse.model_validate(result)
