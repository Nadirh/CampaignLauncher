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
