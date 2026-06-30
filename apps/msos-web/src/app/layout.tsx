import type { Metadata } from "next";
import "./globals.css";

import { NavigationProgressProvider } from "@/components/NavigationProgressProvider";
import { PostAuthReturnHandler } from "@/components/PostAuthReturnHandler";
import { ProductUsageBeacon } from "@/components/ProductUsageBeacon";

export const metadata: Metadata = {
  title: "Market Structure OS",
  description:
    "Compare your market thesis with what options imply — explore structures without hiding assumptions.",
  icons: {
    icon: [{ url: "/brand/msos-mark-color.svg", type: "image/svg+xml" }],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <NavigationProgressProvider>
          <ProductUsageBeacon />
          <PostAuthReturnHandler />
          {children}
        </NavigationProgressProvider>
      </body>
    </html>
  );
}
