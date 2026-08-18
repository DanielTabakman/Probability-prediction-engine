import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "PitchPacks — Devinder Original | Daniel Tabakman",
  description:
    "Playable copy of Devinder Butani's original PitchPacks prototype for comparison with the newer autobattler experiment.",
};

const DEVINDER_PITCHPACKS_URL = "https://devenderbutani21.github.io/PitchPacks/";

export default function DevinderPitchPacksPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#020617",
        color: "#f8fafc",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <header
        style={{
          minHeight: 52,
          padding: "10px 18px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 10,
          borderBottom: "1px solid #1e293b",
          background: "#020617",
          fontSize: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Link
            href="/daniel"
            style={{ color: "#94a3b8", textDecoration: "none", fontWeight: 700 }}
          >
            ← Daniel&apos;s labs
          </Link>
          <span style={{ color: "#475569" }}>|</span>
          <Link
            href="/daniel/pitchpacks"
            style={{ color: "#67e8f9", textDecoration: "none", fontWeight: 700 }}
          >
            Play our autobattler →
          </Link>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ color: "#64748b" }}>
            Devinder&apos;s original · July 2026 build
          </span>
          <a
            href={DEVINDER_PITCHPACKS_URL}
            target="_blank"
            rel="noreferrer"
            style={{ color: "#94a3b8", textDecoration: "none", fontWeight: 700 }}
          >
            Upstream source ↗
          </a>
        </div>
      </header>

      <iframe
        title="Devinder Butani's original PitchPacks prototype"
        src="/daniel/pitchpacks-devinder/game"
        allow="fullscreen"
        style={{
          display: "block",
          width: "100%",
          flex: 1,
          minHeight: "calc(100vh - 53px)",
          border: 0,
          background: "#020617",
        }}
      />
    </main>
  );
}
