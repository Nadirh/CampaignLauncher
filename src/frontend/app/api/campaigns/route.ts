import { NextRequest, NextResponse } from "next/server";
import { fetchFromApi } from "@/lib/api";
import type { CampaignListResponse, Campaign } from "@/types/campaign";

export async function GET() {
  try {
    const data = await fetchFromApi<CampaignListResponse>("/api/campaigns");
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Failed to fetch campaigns" },
      { status: 502 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const data = await fetchFromApi<Campaign>("/api/campaigns", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return NextResponse.json(data, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: "Failed to create campaign" },
      { status: 502 },
    );
  }
}
