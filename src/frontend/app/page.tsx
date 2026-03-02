export const dynamic = "force-dynamic";

import { fetchFromApi } from "@/lib/api";

interface HealthResponse {
  status: string;
  service: string;
}

async function getBackendHealth(): Promise<HealthResponse> {
  try {
    return await fetchFromApi<HealthResponse>("/api/health");
  } catch {
    return { status: "unreachable", service: "campaign-launcher-api" };
  }
}

export default async function HomePage() {
  const health = await getBackendHealth();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">CampaignLauncher</h1>
      <p className="mt-4 text-lg text-gray-600">
        AI-powered paid search campaign builder
      </p>
      <p className="mt-6 text-sm">
        Backend Status:{" "}
        <span
          className={health.status === "ok" ? "text-green-600" : "text-red-600"}
        >
          {health.status}
        </span>
      </p>
    </main>
  );
}
