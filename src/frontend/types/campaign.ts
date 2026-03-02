export type CampaignStatus =
  | "draft"
  | "review"
  | "approved"
  | "launched"
  | "paused";

export type BiddingStrategy =
  | "manual_cpc"
  | "maximize_clicks"
  | "maximize_conversions"
  | "target_cpa"
  | "target_roas";

export interface Campaign {
  id: string;
  name: string;
  landing_page_url: string;
  status: CampaignStatus;
  bidding_strategy: BiddingStrategy;
  daily_budget: number | null;
  created_at: string;
  updated_at: string;
}

export interface CampaignCreate {
  name: string;
  landing_page_url: string;
  bidding_strategy?: BiddingStrategy;
  daily_budget?: number | null;
}

export interface CampaignListResponse {
  campaigns: Campaign[];
  total: number;
}

export type MatchType = "broad" | "phrase" | "exact";

export interface KeywordResponse {
  id: string;
  text: string;
  match_type: MatchType;
  bid: number | null;
  ad_group_id: string;
}

export interface AdResponse {
  id: string;
  final_url: string;
  headlines: Array<{ text: string; position?: number | null }>;
  descriptions: Array<{ text: string }>;
  path1: string | null;
  path2: string | null;
  ad_group_id: string;
}

export interface AdGroupResponse {
  id: string;
  name: string;
  campaign_id: string;
  keywords: KeywordResponse[];
  ads: AdResponse[];
}

export interface GenerateResponse {
  id: string;
  name: string;
  landing_page_url: string;
  status: CampaignStatus;
  bidding_strategy: BiddingStrategy;
  daily_budget: number | null;
  created_at: string;
  updated_at: string;
  ad_groups: AdGroupResponse[];
}
