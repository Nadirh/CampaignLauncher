"use client";

import { useState } from "react";

interface AdsScriptDisplayProps {
  script: string;
  campaignName: string;
  adGroupCount: number;
  keywordCount: number;
  adCount: number;
  onClose: () => void;
}

const INSTRUCTIONS = [
  "In Google Ads, go to Tools > Bulk Actions > Scripts",
  "Click the + button to create a new script",
  "Paste the entire script below into the editor",
  "Click Authorize and grant the required permissions",
  "Click Preview to test without making changes",
  "Click Run to create the campaign (it will be created in PAUSED status)",
];

export default function AdsScriptDisplay({
  script,
  campaignName,
  adGroupCount,
  keywordCount,
  adCount,
  onClose,
}: AdsScriptDisplayProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Google Ads Script</h2>
        <button
          onClick={onClose}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
        >
          Close
        </button>
      </div>

      <p className="text-sm text-gray-600">
        Campaign: <span className="font-medium">{campaignName}</span>
        {" -- "}
        {adGroupCount} ad group{adGroupCount !== 1 ? "s" : ""}, {keywordCount}{" "}
        keyword{keywordCount !== 1 ? "s" : ""}, {adCount} ad
        {adCount !== 1 ? "s" : ""}
      </p>

      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <h3 className="mb-2 text-sm font-medium text-blue-900">
          How to use this script
        </h3>
        <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
          {INSTRUCTIONS.map((instruction, i) => (
            <li key={i}>{instruction}</li>
          ))}
        </ol>
      </div>

      <div className="relative">
        <button
          onClick={handleCopy}
          className="absolute right-2 top-2 rounded-md bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm border border-gray-300 hover:bg-gray-50"
        >
          {copied ? "Copied!" : "Copy Script"}
        </button>
        <pre className="max-h-96 overflow-auto rounded-lg border border-gray-300 bg-gray-900 p-4 pt-12 text-sm text-green-400">
          <code>{script}</code>
        </pre>
      </div>
    </div>
  );
}
