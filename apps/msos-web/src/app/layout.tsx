import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Market Structure OS",
  description:
    "Market Structure OS — compare what you believe to what BTC options imply.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
