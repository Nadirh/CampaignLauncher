import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await params;
    const response = await fetch(`${API_URL}/api/campaigns/${id}/export`);

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to export campaign" },
        { status: response.status },
      );
    }

    const blob = await response.arrayBuffer();
    const headers = new Headers();
    const contentType = response.headers.get("content-type");
    const contentDisposition = response.headers.get("content-disposition");

    if (contentType) {
      headers.set("Content-Type", contentType);
    }
    if (contentDisposition) {
      headers.set("Content-Disposition", contentDisposition);
    }

    return new NextResponse(blob, { status: 200, headers });
  } catch {
    return NextResponse.json(
      { error: "Failed to export campaign" },
      { status: 502 },
    );
  }
}
