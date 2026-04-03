import type { ReactNode } from "react";
import type { Metadata } from "next";

import "@/app/globals.css";

export const metadata: Metadata = {
  title: "F1 Intelligence Hub",
  description: "Race-week F1 intelligence with source-backed summaries and explicit editorial boundaries.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
