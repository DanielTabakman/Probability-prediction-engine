import type { Metadata } from "next";

import { homepageMetadata } from "@/content/homepage";
import "./globals.css";

export const metadata: Metadata = {
  title: homepageMetadata.title,
  description: homepageMetadata.description,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
