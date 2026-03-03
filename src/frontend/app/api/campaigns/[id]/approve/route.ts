import { NextRequest, NextResponse } from "next/server";
import { fetchFromApi } from "@/lib/api";
import type { Campaign } from "@/types/campaign";

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    const data = await fetchFromApi<Campaign>(`/api/campaigns/${id}/approve`, {
      method: "POST",
    });
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Failed to approve campaign" },
      { status: 502 },
    );
  }
}
