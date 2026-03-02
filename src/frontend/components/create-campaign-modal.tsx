"use client";

import { FormEvent, useState } from "react";
import { useCreateCampaign } from "@/hooks/use-campaigns";

interface CreateCampaignModalProps {
  open: boolean;
  onClose: () => void;
}

export default function CreateCampaignModal({
  open,
  onClose,
}: CreateCampaignModalProps) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const mutation = useCreateCampaign();

  if (!open) return null;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    mutation.mutate(
      { name, landing_page_url: url },
      {
        onSuccess: () => {
          setName("");
          setUrl("");
          onClose();
        },
      },
    );
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Create campaign"
    >
      <div
        className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl"
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
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
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
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
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
              onClick={onClose}
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
