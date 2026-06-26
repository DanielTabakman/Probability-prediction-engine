import type { Metadata } from "next";
import "./globals.css";

import { PostAuthReturnHandler } from "@/components/PostAuthReturnHandler";

export const metadata: Metadata = {
  title: "Market Structure OS",
  description:
    "Compare your market thesis with what options imply — explore structures without hiding assumptions.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <PostAuthReturnHandler />
        {children}
      </body>
    </html>
  );
}
