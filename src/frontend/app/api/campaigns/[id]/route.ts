import { NextRequest, NextResponse } from "next/server";
import { fetchFromApi } from "@/lib/api";
import type { Campaign } from "@/types/campaign";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    const data = await fetchFromApi<Campaign>(`/api/campaigns/${id}`);
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Failed to fetch campaign" },
      { status: 502 },
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    const body = await request.json();
    const data = await fetchFromApi<Campaign>(`/api/campaigns/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
    });
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Failed to update campaign" },
      { status: 502 },
    );
  }
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    await fetchFromApi(`/api/campaigns/${id}`, { method: "DELETE" });
    return new NextResponse(null, { status: 204 });
  } catch {
    return NextResponse.json(
      { error: "Failed to delete campaign" },
      { status: 502 },
    );
  }
}
