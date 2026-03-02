import { NextRequest, NextResponse } from "next/server";
import { fetchFromApi } from "@/lib/api";
import type { GenerateResponse } from "@/types/campaign";

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    const data = await fetchFromApi<GenerateResponse>(
      `/api/campaigns/${id}/generate`,
      { method: "POST" },
    );
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Failed to generate campaign" },
      { status: 502 },
    );
  }
}
