import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "PitchPacks — Football Autobattler | Daniel Tabakman",
  description:
    "Playable football autobattler prototype: choose five starters and one bench player, then watch them fight while live sports events buff the corresponding fighters.",
};

export default function PitchPacksPrototypePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#071018",
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
          Football field prototype · drag/drop lineup · fake live feed
        </span>
      </header>
      <iframe
        title="PitchPacks football autobattler prototype"
        src="/daniel/pitchpacks-prototype.html"
        style={{
          display: "block",
          width: "100%",
          flex: 1,
          minHeight: "calc(100vh - 49px)",
          border: 0,
          background: "#071018",
        }}
      />
    </main>
  );
}
