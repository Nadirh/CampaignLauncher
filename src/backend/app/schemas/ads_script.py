from pydantic import BaseModel


class ParsedKeyword(BaseModel):
    ad_group: str
    text: str
    match_type: str
    bid: float | None = None


class ParsedHeadline(BaseModel):
    text: str
    pin_position: int | None = None


class ParsedDescription(BaseModel):
    text: str


class ParsedAd(BaseModel):
    ad_group: str
    ad_number: int
    headlines: list[ParsedHeadline]
    descriptions: list[ParsedDescription]
    final_url: str
    path1: str | None = None
    path2: str | None = None


class ParsedCampaign(BaseModel):
    name: str
    landing_page_url: str
    bidding_strategy: str
    daily_budget: float
    match_types: list[str] | None = None
    negative_keywords: list[str] | None = None
    bid_value: float | None = None
    location_targeting: str | None = None


class ParsedWorkbook(BaseModel):
    campaign: ParsedCampaign
    keywords: list[ParsedKeyword]
    ads: list[ParsedAd]


class ScriptGenerateResponse(BaseModel):
    script: str
    campaign_name: str
    ad_group_count: int
    keyword_count: int
    ad_count: int
