import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import AdsScriptDisplay from "@/components/ads-script-display";

const defaultProps = {
  script: "function main() { /* test script */ }",
  campaignName: "Test Campaign",
  adGroupCount: 3,
  keywordCount: 15,
  adCount: 6,
  onClose: vi.fn(),
};

beforeEach(() => {
  vi.restoreAllMocks();
});

describe("AdsScriptDisplay", () => {
  it("displays campaign name and counts", () => {
    render(<AdsScriptDisplay {...defaultProps} />);
    expect(screen.getByText("Test Campaign")).toBeInTheDocument();
    expect(screen.getByText(/3 ad groups/)).toBeInTheDocument();
    expect(screen.getByText(/15 keywords/)).toBeInTheDocument();
    expect(screen.getByText(/6 ads/)).toBeInTheDocument();
  });

  it("displays the script text", () => {
    render(<AdsScriptDisplay {...defaultProps} />);
    expect(
      screen.getByText("function main() { /* test script */ }"),
    ).toBeInTheDocument();
  });

  it("displays instructions", () => {
    render(<AdsScriptDisplay {...defaultProps} />);
    expect(screen.getByText(/Bulk Actions/)).toBeInTheDocument();
    expect(screen.getByText(/Paste the entire script/)).toBeInTheDocument();
    expect(screen.getByText(/Click Preview/)).toBeInTheDocument();
  });

  it("copy button calls clipboard API", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(<AdsScriptDisplay {...defaultProps} />);
    fireEvent.click(screen.getByText("Copy Script"));
    expect(writeText).toHaveBeenCalledWith(defaultProps.script);
  });

  it("close button calls onClose", () => {
    const onClose = vi.fn();
    render(<AdsScriptDisplay {...defaultProps} onClose={onClose} />);
    fireEvent.click(screen.getByText("Close"));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
