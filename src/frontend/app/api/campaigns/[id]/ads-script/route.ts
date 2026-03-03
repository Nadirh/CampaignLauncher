import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    const formData = await request.formData();

    const response = await fetch(`${API_URL}/api/campaigns/${id}/ads-script`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const body = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      return NextResponse.json(
        { error: body.detail || "Failed to generate ads script" },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Failed to generate ads script" },
      { status: 502 },
    );
  }
}
