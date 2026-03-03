import uuid
from datetime import datetime

from pydantic import BaseModel, HttpUrl

from app.models.campaign import BiddingStrategy, CampaignStatus


class CampaignCreate(BaseModel):
    name: str
    landing_page_url: HttpUrl
    bidding_strategy: BiddingStrategy
    daily_budget: float
    match_types: list[str]
    negative_keywords: list[str] | None = None
    bid_value: float
    location_targeting: str


class CampaignUpdate(BaseModel):
    name: str | None = None
    landing_page_url: HttpUrl | None = None
    status: CampaignStatus | None = None
    bidding_strategy: BiddingStrategy | None = None
    daily_budget: float | None = None
    match_types: list[str] | None = None
    negative_keywords: list[str] | None = None
    bid_value: float | None = None
    location_targeting: str | None = None


class CampaignResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    landing_page_url: str
    status: CampaignStatus
    bidding_strategy: BiddingStrategy
    daily_budget: float | None
    match_types: list[str] | None = None
    negative_keywords: list[str] | None = None
    bid_value: float | None = None
    location_targeting: str | None = None
    created_at: datetime
    updated_at: datetime


class CampaignListResponse(BaseModel):
    campaigns: list[CampaignResponse]
    total: int
