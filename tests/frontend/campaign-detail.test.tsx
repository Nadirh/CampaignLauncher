import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

const mockPush = vi.fn();

vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "test-id-123" }),
  useRouter: () => ({ push: mockPush }),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

import CampaignDetailPage from "@/app/campaigns/[id]/page";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

const mockCampaign = {
  id: "test-id-123",
  name: "Test Campaign",
  landing_page_url: "https://example.com",
  status: "review" as const,
  bidding_strategy: "target_cpa" as const,
  daily_budget: 50,
  match_types: ["phrase", "exact"],
  negative_keywords: ["free"],
  bid_value: 2.5,
  location_targeting: "US",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  ad_groups: [
    {
      id: "ag-1",
      name: "Ad Group 1",
      campaign_id: "test-id-123",
      keywords: [
        { id: "kw-1", text: "test keyword", match_type: "phrase" as const, bid: null, ad_group_id: "ag-1" },
      ],
      ads: [
        {
          id: "ad-1",
          final_url: "https://example.com",
          headlines: [
            { text: "Headline 1", position: 1, trigger: "urgency" },
            { text: "Headline 2", position: null, trigger: null },
          ],
          descriptions: [{ text: "Description 1", trigger: "social proof" }],
          path1: "path1",
          path2: "path2",
          ad_group_id: "ag-1",
        },
      ],
    },
  ],
};

beforeEach(() => {
  vi.restoreAllMocks();
});

describe("CampaignDetailPage", () => {
  it("shows loading state initially", () => {
    vi.spyOn(global, "fetch").mockImplementation(
      () => new Promise(() => {}),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading campaign...")).toBeInTheDocument();
  });

  it("renders campaign data with ad groups", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Test Campaign")).toBeInTheDocument();
    });
    expect(screen.getByText("review")).toBeInTheDocument();
    expect(screen.getByText("Ad Group 1")).toBeInTheDocument();
    expect(screen.getByText("test keyword")).toBeInTheDocument();
    expect(screen.getByText("Headline 1")).toBeInTheDocument();
    expect(screen.getByText("Description 1")).toBeInTheDocument();
  });

  it("shows approve and reject buttons for review status", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Approve")).toBeInTheDocument();
    });
    expect(screen.getByText("Reject")).toBeInTheDocument();
  });

  it("hides approve and reject buttons for non-review status", async () => {
    const draftCampaign = { ...mockCampaign, status: "draft", ad_groups: [] };
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(draftCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Test Campaign")).toBeInTheDocument();
    });
    expect(screen.queryByText("Approve")).not.toBeInTheDocument();
    expect(screen.queryByText("Reject")).not.toBeInTheDocument();
  });

  it("opens approve confirmation modal", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Approve")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Approve"));
    expect(screen.getByText("Approve Campaign")).toBeInTheDocument();
  });

  it("opens reject confirmation modal", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Reject")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Reject"));
    expect(screen.getByText("Reject Campaign")).toBeInTheDocument();
  });

  it("shows Download Excel button when ad groups exist", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Download Excel")).toBeInTheDocument();
    });
  });

  it("hides Download Excel button when no ad groups", async () => {
    const emptyCampaign = { ...mockCampaign, status: "draft", ad_groups: [] };
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(emptyCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Test Campaign")).toBeInTheDocument();
    });
    expect(screen.queryByText("Download Excel")).not.toBeInTheDocument();
  });

  it("shows pin position badge and trigger on headlines", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Pin 1")).toBeInTheDocument();
    });
    expect(screen.getByText("-- urgency")).toBeInTheDocument();
  });

  it("shows trigger on descriptions", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("-- social proof")).toBeInTheDocument();
    });
  });

  it("shows campaign settings in header", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockCampaign), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignDetailPage />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Match: phrase, exact")).toBeInTheDocument();
    });
    expect(screen.getByText("Bid: $2.5")).toBeInTheDocument();
    expect(screen.getByText("Location: US")).toBeInTheDocument();
    expect(screen.getByText("Negatives: free")).toBeInTheDocument();
  });
});
