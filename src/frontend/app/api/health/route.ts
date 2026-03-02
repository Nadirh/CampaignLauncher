import { NextResponse } from "next/server";
import { fetchFromApi } from "@/lib/api";

interface HealthResponse {
  status: string;
  service: string;
}

export async function GET() {
  try {
    const data = await fetchFromApi<HealthResponse>("/api/health");
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { status: "error", service: "campaign-launcher-api" },
      { status: 502 },
    );
  }
}
