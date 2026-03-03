import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.campaign import BiddingStrategy, CampaignStatus
from app.models.keyword import MatchType


# -- Page fetcher output --


class PageContent(BaseModel):
    url: str
    title: str = ""
    meta_description: str = ""
    headings: list[str] = []
    hero_text: str = ""
    ctas: list[str] = []
    features: list[str] = []
    raw_text: str = ""


# -- Claude analyzer output (parsed from JSON) --


class KeywordData(BaseModel):
    text: str
    match_type: MatchType = MatchType.PHRASE


class HeadlineData(BaseModel):
    text: str
    position: int | None = None
    trigger: str | None = None


class DescriptionData(BaseModel):
    text: str
    trigger: str | None = None


class AdGroupData(BaseModel):
    name: str
    keywords: list[KeywordData]
    headlines: list[HeadlineData]
    descriptions: list[DescriptionData]


class CampaignStructure(BaseModel):
    ad_groups: list[AdGroupData]


# -- API response schemas --


class KeywordResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    text: str
    match_type: MatchType
    bid: float | None
    ad_group_id: uuid.UUID


class AdResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    final_url: str
    headlines: list
    descriptions: list
    path1: str | None
    path2: str | None
    ad_group_id: uuid.UUID


class AdGroupResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    campaign_id: uuid.UUID
    keywords: list[KeywordResponse] = []
    ads: list[AdResponse] = []


class CampaignGenerateResponse(BaseModel):
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
    ad_groups: list[AdGroupResponse] = []
