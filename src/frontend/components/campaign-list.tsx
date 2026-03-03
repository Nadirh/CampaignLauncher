"use client";

import { useState } from "react";
import Link from "next/link";
import { useCampaigns, useGenerateCampaign } from "@/hooks/use-campaigns";
import CreateCampaignModal from "@/components/create-campaign-modal";

export default function CampaignList() {
  const { data, isLoading, isError } = useCampaigns();
  const [modalOpen, setModalOpen] = useState(false);
  const generateMutation = useGenerateCampaign();

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <button
          onClick={() => setModalOpen(true)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          New Campaign
        </button>
      </div>

      {isLoading && <p className="mt-6 text-gray-500">Loading campaigns...</p>}

      {isError && (
        <p className="mt-6 text-red-600">
          Failed to load campaigns. Please try again.
        </p>
      )}

      {data && data.total === 0 && (
        <p className="mt-6 text-gray-500">
          No campaigns yet. Create your first campaign to get started.
        </p>
      )}

      {data && data.total > 0 && (
        <table className="mt-6 w-full text-left text-sm">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="pb-2 font-medium">Name</th>
              <th className="pb-2 font-medium">Status</th>
              <th className="pb-2 font-medium">URL</th>
              <th className="pb-2 font-medium">Created</th>
              <th className="pb-2 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.campaigns.map((campaign) => (
              <tr key={campaign.id} className="border-b">
                <td className="py-3 font-medium">
                  <Link
                    href={`/campaigns/${campaign.id}`}
                    className="text-blue-600 hover:underline"
                  >
                    {campaign.name}
                  </Link>
                </td>
                <td className="py-3">
                  <span className="rounded-full bg-gray-100 px-2 py-1 text-xs capitalize">
                    {campaign.status}
                  </span>
                </td>
                <td className="py-3 max-w-xs truncate text-gray-500">
                  {campaign.landing_page_url}
                </td>
                <td className="py-3 text-gray-500">
                  {new Date(campaign.created_at).toLocaleDateString()}
                </td>
                <td className="py-3">
                  {campaign.status === "draft" && (
                    <button
                      onClick={() => generateMutation.mutate(campaign.id)}
                      disabled={generateMutation.isPending}
                      className="rounded-md bg-green-600 px-3 py-1 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
                    >
                      {generateMutation.isPending
                        ? "Generating..."
                        : "Generate"}
                    </button>
                  )}
                  {campaign.status === "review" && (
                    <Link
                      href={`/campaigns/${campaign.id}`}
                      className="rounded-md bg-yellow-500 px-3 py-1 text-xs font-medium text-white hover:bg-yellow-600"
                    >
                      Review
                    </Link>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {generateMutation.isError && (
        <p className="mt-4 text-red-600">
          Generation failed. Please try again.
        </p>
      )}

      <CreateCampaignModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
}
