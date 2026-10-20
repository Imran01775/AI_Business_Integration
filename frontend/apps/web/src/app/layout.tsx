import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI Sales Agent",
  description: "AI-assisted sales for messenger businesses",
  manifest: "/manifest.webmanifest",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
