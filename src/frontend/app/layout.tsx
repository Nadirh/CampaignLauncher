import type { Metadata } from "next";
import QueryProvider from "@/providers/query-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "CampaignLauncher",
  description: "AI-powered paid search campaign builder",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className="min-h-screen bg-white text-gray-900 antialiased"
        suppressHydrationWarning
      >
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
