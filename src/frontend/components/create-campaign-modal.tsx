"use client";

import { FormEvent, useState } from "react";
import { useCreateCampaign } from "@/hooks/use-campaigns";
import type { BiddingStrategy } from "@/types/campaign";

interface CreateCampaignModalProps {
  open: boolean;
  onClose: () => void;
}

const MATCH_TYPE_OPTIONS = ["broad", "phrase", "exact"] as const;

export default function CreateCampaignModal({
  open,
  onClose,
}: CreateCampaignModalProps) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [matchTypes, setMatchTypes] = useState<string[]>(["phrase", "exact"]);
  const [biddingStrategy, setBiddingStrategy] =
    useState<BiddingStrategy>("target_cpa");
  const [bidValue, setBidValue] = useState("");
  const [dailyBudget, setDailyBudget] = useState("");
  const [negativeKeywords, setNegativeKeywords] = useState("");
  const [locationTargeting, setLocationTargeting] = useState("");
  const mutation = useCreateCampaign();

  if (!open) return null;

  function resetForm() {
    setName("");
    setUrl("");
    setMatchTypes(["phrase", "exact"]);
    setBiddingStrategy("target_cpa");
    setBidValue("");
    setDailyBudget("");
    setNegativeKeywords("");
    setLocationTargeting("");
  }

  function handleMatchTypeToggle(type: string) {
    setMatchTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type],
    );
  }

  const matchTypesValid = matchTypes.length > 0;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!matchTypesValid) return;
    const negKw = negativeKeywords
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    mutation.mutate(
      {
        name,
        landing_page_url: url,
        bidding_strategy: biddingStrategy,
        daily_budget: parseFloat(dailyBudget),
        match_types: matchTypes,
        negative_keywords: negKw.length > 0 ? negKw : null,
        bid_value: parseFloat(bidValue),
        location_targeting: locationTargeting,
      },
      {
        onSuccess: () => {
          resetForm();
          onClose();
        },
      },
    );
  }

  function handleClose() {
    resetForm();
    onClose();
  }

  const inputClass =
    "mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-label="Create campaign"
    >
      <div
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-lg bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold">New Campaign</h2>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label
              htmlFor="campaign-name"
              className="block text-sm font-medium text-gray-700"
            >
              Campaign Name
            </label>
            <input
              id="campaign-name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label
              htmlFor="landing-page-url"
              className="block text-sm font-medium text-gray-700"
            >
              Landing Page URL
            </label>
            <input
              id="landing-page-url"
              type="url"
              required
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className={inputClass}
            />
          </div>

          {/* Campaign Settings */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-800">
              Campaign Settings
            </h3>
          </div>

          <div>
            <span className="block text-sm font-medium text-gray-700">
              Match Types <span className="text-red-500">*</span>
            </span>
            <div className="mt-1 flex gap-4">
              {MATCH_TYPE_OPTIONS.map((type) => (
                <label key={type} className="flex items-center gap-1.5 text-sm">
                  <input
                    type="checkbox"
                    checked={matchTypes.includes(type)}
                    onChange={() => handleMatchTypeToggle(type)}
                    className="rounded border-gray-300"
                  />
                  {type}
                </label>
              ))}
            </div>
            {!matchTypesValid && (
              <p className="mt-1 text-xs text-red-500">
                Select at least one match type.
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="bidding-strategy"
              className="block text-sm font-medium text-gray-700"
            >
              Bidding Strategy
            </label>
            <select
              id="bidding-strategy"
              value={biddingStrategy}
              onChange={(e) =>
                setBiddingStrategy(e.target.value as BiddingStrategy)
              }
              className={inputClass}
            >
              <option value="target_cpa">Target CPA</option>
              <option value="maximize_conversions">Maximize Conversions</option>
              <option value="maximize_clicks">Maximize Clicks</option>
              <option value="manual_cpc">Manual CPC</option>
              <option value="target_roas">Target ROAS</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="bid-value"
              className="block text-sm font-medium text-gray-700"
            >
              Bid Value ($) <span className="text-red-500">*</span>
            </label>
            <input
              id="bid-value"
              type="number"
              step="0.01"
              min="0.01"
              required
              value={bidValue}
              onChange={(e) => setBidValue(e.target.value)}
              placeholder="e.g. 2.50"
              className={inputClass}
            />
          </div>

          <div>
            <label
              htmlFor="daily-budget"
              className="block text-sm font-medium text-gray-700"
            >
              Daily Budget ($) <span className="text-red-500">*</span>
            </label>
            <input
              id="daily-budget"
              type="number"
              step="0.01"
              min="0.01"
              required
              value={dailyBudget}
              onChange={(e) => setDailyBudget(e.target.value)}
              placeholder="e.g. 50.00"
              className={inputClass}
            />
          </div>

          <div>
            <label
              htmlFor="negative-keywords"
              className="block text-sm font-medium text-gray-700"
            >
              Negative Keywords
            </label>
            <input
              id="negative-keywords"
              type="text"
              value={negativeKeywords}
              onChange={(e) => setNegativeKeywords(e.target.value)}
              placeholder="Comma-separated, e.g. free, cheap"
              className={inputClass}
            />
          </div>

          <div>
            <label
              htmlFor="location-targeting"
              className="block text-sm font-medium text-gray-700"
            >
              Location Targeting <span className="text-red-500">*</span>
            </label>
            <input
              id="location-targeting"
              type="text"
              required
              value={locationTargeting}
              onChange={(e) => setLocationTargeting(e.target.value)}
              placeholder="e.g. US, UK, California"
              className={inputClass}
            />
          </div>

          {mutation.isError && (
            <p className="text-sm text-red-600">
              Failed to create campaign. Please try again.
            </p>
          )}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handleClose}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {mutation.isPending ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
