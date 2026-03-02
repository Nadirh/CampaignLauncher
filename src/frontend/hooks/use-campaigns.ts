import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  Campaign,
  CampaignCreate,
  CampaignListResponse,
  GenerateResponse,
} from "@/types/campaign";

const CAMPAIGNS_KEY = ["campaigns"] as const;

async function fetchCampaigns(): Promise<CampaignListResponse> {
  const res = await fetch("/api/campaigns");
  if (!res.ok) throw new Error("Failed to fetch campaigns");
  return res.json();
}

async function createCampaign(data: CampaignCreate): Promise<Campaign> {
  const res = await fetch("/api/campaigns", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create campaign");
  return res.json();
}

export function useCampaigns() {
  return useQuery({
    queryKey: CAMPAIGNS_KEY,
    queryFn: fetchCampaigns,
  });
}

export function useCreateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createCampaign,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CAMPAIGNS_KEY });
    },
  });
}

async function generateCampaign(campaignId: string): Promise<GenerateResponse> {
  const res = await fetch(`/api/campaigns/${campaignId}/generate`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to generate campaign");
  return res.json();
}

export function useGenerateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: generateCampaign,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CAMPAIGNS_KEY });
    },
  });
}
