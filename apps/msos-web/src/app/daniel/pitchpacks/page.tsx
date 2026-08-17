import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "PitchPacks — Live Sports Autobattler | Daniel Tabakman",
  description:
    "Playable prototype: 5v5 autobattler where live sports events buff the corresponding fighters in real time.",
};

export default function PitchPacksPrototypePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#080b12",
        color: "#f8fafc",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <header
        style={{
          minHeight: 48,
          padding: "10px 18px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          borderBottom: "1px solid #1f2937",
          background: "#070b12",
          fontSize: 12,
        }}
      >
        <Link
          href="/daniel"
          style={{ color: "#94a3b8", textDecoration: "none", fontWeight: 700 }}
        >
          ← Daniel&apos;s labs
        </Link>
        <span style={{ color: "#64748b" }}>
          Prototype · fake sports feed · mechanic test
        </span>
      </header>
      <iframe
        title="PitchPacks live sports autobattler prototype"
        src="/daniel/pitchpacks-prototype.html"
        style={{
          display: "block",
          width: "100%",
          flex: 1,
          minHeight: "calc(100vh - 49px)",
          border: 0,
          background: "#080b12",
        }}
      />
    </main>
  );
}
