import uuid
from datetime import datetime

from pydantic import BaseModel, HttpUrl

from app.models.campaign import BiddingStrategy, CampaignStatus


class CampaignCreate(BaseModel):
    name: str
    landing_page_url: HttpUrl
    bidding_strategy: BiddingStrategy = BiddingStrategy.MANUAL_CPC
    daily_budget: float | None = None


class CampaignUpdate(BaseModel):
    name: str | None = None
    landing_page_url: HttpUrl | None = None
    status: CampaignStatus | None = None
    bidding_strategy: BiddingStrategy | None = None
    daily_budget: float | None = None


class CampaignResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    landing_page_url: str
    status: CampaignStatus
    bidding_strategy: BiddingStrategy
    daily_budget: float | None
    created_at: datetime
    updated_at: datetime


class CampaignListResponse(BaseModel):
    campaigns: list[CampaignResponse]
    total: int
