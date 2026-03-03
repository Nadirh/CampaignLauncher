"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  useCampaignDetail,
  useApproveCampaign,
  useRejectCampaign,
  useGenerateAdsScript,
} from "@/hooks/use-campaigns";
import ConfirmModal from "@/components/confirm-modal";
import AdsScriptDisplay from "@/components/ads-script-display";
import type { AdGroupResponse, ScriptResponse } from "@/types/campaign";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  review: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  launched: "bg-blue-100 text-blue-800",
  paused: "bg-red-100 text-red-700",
};

const MATCH_TYPE_COLORS: Record<string, string> = {
  broad: "bg-gray-100 text-gray-600",
  phrase: "bg-blue-50 text-blue-700",
  exact: "bg-purple-50 text-purple-700",
};

function AdGroupSection({ adGroup }: { adGroup: AdGroupResponse }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="rounded-lg border border-gray-200">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-gray-50"
      >
        <h3 className="font-medium">{adGroup.name}</h3>
        <span className="text-sm text-gray-500">
          {expanded ? "Collapse" : "Expand"}
        </span>
      </button>

      {expanded && (
        <div className="border-t px-4 py-4 space-y-6">
          {/* Keywords */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">
              Keywords ({adGroup.keywords.length})
            </h4>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-gray-500">
                  <th className="pb-1 text-left font-medium">Keyword</th>
                  <th className="pb-1 text-left font-medium">Match Type</th>
                </tr>
              </thead>
              <tbody>
                {adGroup.keywords.map((kw) => (
                  <tr key={kw.id} className="border-b last:border-0">
                    <td className="py-1.5">{kw.text}</td>
                    <td className="py-1.5">
                      <span
                        className={`rounded px-1.5 py-0.5 text-xs ${MATCH_TYPE_COLORS[kw.match_type] || ""}`}
                      >
                        {kw.match_type}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Ads */}
          {adGroup.ads.map((ad, adIndex) => (
            <div key={ad.id}>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Ad {adIndex + 1}
              </h4>
              <div className="rounded border border-gray-200 bg-gray-50 p-3 space-y-2">
                <div>
                  <span className="text-xs font-medium text-gray-500">
                    Headlines
                  </span>
                  <ol className="mt-1 list-decimal list-inside text-sm">
                    {ad.headlines.map((h, i) => (
                      <li key={i}>
                        {h.position != null && (
                          <span className="mr-1 inline-block rounded bg-indigo-100 px-1.5 py-0.5 text-xs text-indigo-700">
                            Pin {h.position}
                          </span>
                        )}
                        {h.text}
                        {h.trigger && (
                          <span className="ml-1 text-xs text-gray-400">
                            -- {h.trigger}
                          </span>
                        )}
                      </li>
                    ))}
                  </ol>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500">
                    Descriptions
                  </span>
                  <ol className="mt-1 list-decimal list-inside text-sm">
                    {ad.descriptions.map((d, i) => (
                      <li key={i}>
                        {d.text}
                        {d.trigger && (
                          <span className="ml-1 text-xs text-gray-400">
                            -- {d.trigger}
                          </span>
                        )}
                      </li>
                    ))}
                  </ol>
                </div>
                {(ad.path1 || ad.path2) && (
                  <div>
                    <span className="text-xs font-medium text-gray-500">
                      URL Paths
                    </span>
                    <p className="mt-1 text-sm">
                      /{ad.path1 || ""}
                      {ad.path2 ? `/${ad.path2}` : ""}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: campaign, isLoading, isError } = useCampaignDetail(id);
  const approveMutation = useApproveCampaign();
  const rejectMutation = useRejectCampaign();
  const scriptMutation = useGenerateAdsScript();

  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(false);
  const [scriptResult, setScriptResult] = useState<ScriptResponse | null>(null);
  const [scriptError, setScriptError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  async function handleExport() {
    setExporting(true);
    setExportError(false);
    try {
      const response = await fetch(`/api/campaigns/${id}/export`);
      if (!response.ok) throw new Error("Export failed");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${campaign?.name?.replace(/\s+/g, "_") || "campaign"}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setExportError(true);
    } finally {
      setExporting(false);
    }
  }

  function handleGenerateScript() {
    if (!selectedFile) return;
    setScriptError(null);
    scriptMutation.mutate(
      { campaignId: id, file: selectedFile },
      {
        onSuccess: (data) => {
          setScriptResult(data);
        },
        onError: (error) => {
          setScriptError(error.message);
        },
      },
    );
  }

  function handleApprove() {
    approveMutation.mutate(id, {
      onSuccess: () => {
        setShowApproveModal(false);
      },
    });
  }

  function handleReject() {
    rejectMutation.mutate(id, {
      onSuccess: () => {
        setShowRejectModal(false);
      },
    });
  }

  if (isLoading) {
    return <p className="text-gray-500">Loading campaign...</p>;
  }

  if (isError || !campaign) {
    return (
      <div>
        <p className="text-red-600">Failed to load campaign.</p>
        <Link
          href="/campaigns"
          className="mt-2 text-sm text-blue-600 hover:underline"
        >
          Back to campaigns
        </Link>
      </div>
    );
  }

  const isReview = campaign.status === "review";

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link href="/campaigns" className="text-sm text-blue-600 hover:underline">
        Back to campaigns
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{campaign.name}</h1>
          <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[campaign.status] || ""}`}
            >
              {campaign.status}
            </span>
            <span>{campaign.bidding_strategy.replace(/_/g, " ")}</span>
            {campaign.daily_budget && <span>${campaign.daily_budget}/day</span>}
          </div>
          <p className="mt-1 text-sm text-gray-500 break-all">
            {campaign.landing_page_url}
          </p>
          {(campaign.match_types ||
            campaign.negative_keywords ||
            campaign.bid_value != null ||
            campaign.location_targeting) && (
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
              {campaign.match_types && (
                <span>Match: {campaign.match_types.join(", ")}</span>
              )}
              {campaign.bid_value != null && (
                <span>Bid: ${campaign.bid_value}</span>
              )}
              {campaign.location_targeting && (
                <span>Location: {campaign.location_targeting}</span>
              )}
              {campaign.negative_keywords && (
                <span>Negatives: {campaign.negative_keywords.join(", ")}</span>
              )}
            </div>
          )}
        </div>

        <div className="flex gap-2">
          {campaign.ad_groups.length > 0 && (
            <button
              onClick={handleExport}
              disabled={exporting}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              {exporting ? "Exporting..." : "Download Excel"}
            </button>
          )}
          {isReview && (
            <>
              <button
                onClick={() => setShowRejectModal(true)}
                className="rounded-md border border-red-300 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50"
              >
                Reject
              </button>
              <button
                onClick={() => setShowApproveModal(true)}
                className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
              >
                Approve
              </button>
            </>
          )}
        </div>
      </div>

      {/* Error messages */}
      {approveMutation.isError && (
        <p className="text-sm text-red-600">Failed to approve campaign.</p>
      )}
      {rejectMutation.isError && (
        <p className="text-sm text-red-600">Failed to reject campaign.</p>
      )}
      {exportError && (
        <p className="text-sm text-red-600">Failed to export campaign.</p>
      )}

      {/* Ad Groups */}
      {campaign.ad_groups.length === 0 ? (
        <p className="text-gray-500">No ad groups generated yet.</p>
      ) : (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">
            Ad Groups ({campaign.ad_groups.length})
          </h2>
          {campaign.ad_groups.map((ag) => (
            <AdGroupSection key={ag.id} adGroup={ag} />
          ))}
        </div>
      )}

      {/* Generate Google Ads Script */}
      {campaign.ad_groups.length > 0 && (
        <div className="space-y-3 rounded-lg border border-gray-200 p-4">
          <h2 className="text-lg font-semibold">Generate Google Ads Script</h2>
          {scriptResult ? (
            <AdsScriptDisplay
              script={scriptResult.script}
              campaignName={scriptResult.campaign_name}
              adGroupCount={scriptResult.ad_group_count}
              keywordCount={scriptResult.keyword_count}
              adCount={scriptResult.ad_count}
              onClose={() => {
                setScriptResult(null);
                setSelectedFile(null);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }}
            />
          ) : (
            <>
              <p className="text-sm text-gray-600">
                Upload a reviewed Excel workbook to generate a Google Ads
                Script.
              </p>
              <div className="flex items-center gap-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="text-sm text-gray-500 file:mr-3 file:rounded-md file:border file:border-gray-300 file:bg-white file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-gray-700 hover:file:bg-gray-50"
                />
                <button
                  onClick={handleGenerateScript}
                  disabled={!selectedFile || scriptMutation.isPending}
                  className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {scriptMutation.isPending
                    ? "Generating..."
                    : "Generate Script"}
                </button>
              </div>
              {scriptError && (
                <p className="text-sm text-red-600">{scriptError}</p>
              )}
            </>
          )}
        </div>
      )}

      {/* Modals */}
      <ConfirmModal
        open={showApproveModal}
        title="Approve Campaign"
        message="Are you sure you want to approve this campaign? It will be marked as ready for launch."
        confirmLabel="Approve"
        confirmClassName="bg-green-600 hover:bg-green-700"
        isPending={approveMutation.isPending}
        onConfirm={handleApprove}
        onCancel={() => setShowApproveModal(false)}
      />
      <ConfirmModal
        open={showRejectModal}
        title="Reject Campaign"
        message="Are you sure you want to reject this campaign? It will be returned to draft status for re-generation."
        confirmLabel="Reject"
        confirmClassName="bg-red-600 hover:bg-red-700"
        isPending={rejectMutation.isPending}
        onConfirm={handleReject}
        onCancel={() => setShowRejectModal(false)}
      />
    </div>
  );
}
