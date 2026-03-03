import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.ad_group import AdGroup
from app.models.campaign import Campaign, CampaignStatus
from app.schemas.campaign import (
    CampaignCreate,
    CampaignListResponse,
    CampaignResponse,
    CampaignUpdate,
)
from app.schemas.pipeline import CampaignGenerateResponse

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(db: AsyncSession = Depends(get_db)) -> CampaignListResponse:
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = list(result.scalars().all())
    return CampaignListResponse(
        campaigns=[CampaignResponse.model_validate(c) for c in campaigns],
        total=len(campaigns),
    )


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    body: CampaignCreate,
    db: AsyncSession = Depends(get_db),
) -> CampaignResponse:
    campaign = Campaign(
        name=body.name,
        landing_page_url=str(body.landing_page_url),
        bidding_strategy=body.bidding_strategy,
        daily_budget=body.daily_budget,
        match_types=body.match_types,
        negative_keywords=body.negative_keywords,
        bid_value=body.bid_value,
        location_targeting=body.location_targeting,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}", response_model=CampaignGenerateResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CampaignGenerateResponse:
    result = await db.execute(
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(
            selectinload(Campaign.ad_groups)
            .selectinload(AdGroup.keywords),
            selectinload(Campaign.ad_groups)
            .selectinload(AdGroup.ads),
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignGenerateResponse.model_validate(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    body: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
) -> CampaignResponse:
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "landing_page_url" and value is not None:
            value = str(value)
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await db.delete(campaign)
    await db.commit()


@router.post("/{campaign_id}/approve", response_model=CampaignResponse)
async def approve_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CampaignResponse:
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != CampaignStatus.REVIEW:
        raise HTTPException(
            status_code=409,
            detail=f"Campaign must be in review status to approve (current: {campaign.status.value})",
        )
    campaign.status = CampaignStatus.APPROVED
    await db.commit()
    await db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.post("/{campaign_id}/reject", response_model=CampaignResponse)
async def reject_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CampaignResponse:
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != CampaignStatus.REVIEW:
        raise HTTPException(
            status_code=409,
            detail=f"Campaign must be in review status to reject (current: {campaign.status.value})",
        )
    campaign.status = CampaignStatus.DRAFT
    await db.commit()
    await db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)
