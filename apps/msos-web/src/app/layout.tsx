import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Market Structure OS",
  description:
    "Market Structure OS — platform for legible market theses. Strategy Lab and PPE preview.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
