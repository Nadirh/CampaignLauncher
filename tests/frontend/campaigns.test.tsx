import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import CampaignList from "@/components/campaign-list";

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

beforeEach(() => {
  vi.restoreAllMocks();
});

describe("CampaignList", () => {
  it("shows loading state initially", () => {
    vi.spyOn(global, "fetch").mockImplementation(
      () => new Promise(() => {}), // never resolves
    );
    render(<CampaignList />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading campaigns...")).toBeInTheDocument();
  });

  it("shows empty state when no campaigns exist", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ campaigns: [], total: 0 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignList />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(
        screen.getByText(/No campaigns yet/),
      ).toBeInTheDocument();
    });
  });

  it("renders campaigns in a table", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          campaigns: [
            {
              id: "abc-123",
              name: "Test Campaign",
              status: "draft",
              landing_page_url: "https://example.com",
              bidding_strategy: "manual_cpc",
              daily_budget: null,
              created_at: "2026-01-01T00:00:00Z",
              updated_at: "2026-01-01T00:00:00Z",
            },
          ],
          total: 1,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    render(<CampaignList />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Test Campaign")).toBeInTheDocument();
    });
    expect(screen.getByText("draft")).toBeInTheDocument();
  });

  it("shows Generate button for draft campaigns", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          campaigns: [
            {
              id: "abc-123",
              name: "Draft Campaign",
              status: "draft",
              landing_page_url: "https://example.com",
              bidding_strategy: "manual_cpc",
              daily_budget: null,
              created_at: "2026-01-01T00:00:00Z",
              updated_at: "2026-01-01T00:00:00Z",
            },
          ],
          total: 1,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    render(<CampaignList />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Generate")).toBeInTheDocument();
    });
  });

  it("hides Generate button for non-draft campaigns", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          campaigns: [
            {
              id: "abc-456",
              name: "Review Campaign",
              status: "review",
              landing_page_url: "https://example.com",
              bidding_strategy: "manual_cpc",
              daily_budget: null,
              created_at: "2026-01-01T00:00:00Z",
              updated_at: "2026-01-01T00:00:00Z",
            },
          ],
          total: 1,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    render(<CampaignList />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText("Review Campaign")).toBeInTheDocument();
    });
    expect(screen.queryByText("Generate")).not.toBeInTheDocument();
  });

  it("opens and closes the create campaign modal", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ campaigns: [], total: 0 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    render(<CampaignList />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("New Campaign")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("New Campaign"));
    expect(screen.getByLabelText("Campaign Name")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Cancel"));
    await waitFor(() => {
      expect(screen.queryByLabelText("Campaign Name")).not.toBeInTheDocument();
    });
  });
});
