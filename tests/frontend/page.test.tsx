import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  fetchFromApi: vi.fn().mockResolvedValue({
    status: "ok",
    service: "campaign-launcher-api",
  }),
}));

describe("HomePage", () => {
  it("renders the heading and backend status", async () => {
    const { default: HomePage } = await import("@/app/page");
    const Page = await HomePage();
    render(Page);

    expect(
      screen.getByRole("heading", { name: "CampaignLauncher" }),
    ).toBeInTheDocument();
    expect(screen.getByText("ok")).toBeInTheDocument();
  });
});
