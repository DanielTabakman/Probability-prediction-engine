/**
 * Client-safe monitor mark formatting (no server/fs imports).
 */

export type MonitorMarkParts = {
  savedSpotUsd?: number;
  currentSpotUsd?: number | null;
  maxLossUsd?: number;
  asOfUtc?: string;
};

function formatTimestamp(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return "—";
  const parsed = Date.parse(trimmed);
  if (Number.isNaN(parsed)) return trimmed;
  return new Date(parsed).toISOString().slice(0, 16).replace("T", " ");
}

export function formatMarkLine(
  parts: MonitorMarkParts,
  formatUsdAmount: (usd: number) => string,
): string | undefined {
  const { savedSpotUsd, currentSpotUsd, maxLossUsd, asOfUtc } = parts;
  if (savedSpotUsd == null && currentSpotUsd == null) {
    return undefined;
  }
  const lines: string[] = [];
  if (typeof savedSpotUsd === "number" && currentSpotUsd != null) {
    lines.push(`Spot ${formatUsdAmount(savedSpotUsd)} → ${formatUsdAmount(currentSpotUsd)}`);
  } else if (typeof savedSpotUsd === "number") {
    lines.push(`Saved at ${formatUsdAmount(savedSpotUsd)}`);
  } else if (currentSpotUsd != null) {
    lines.push(`Spot now ${formatUsdAmount(currentSpotUsd)}`);
  }
  if (typeof maxLossUsd === "number") {
    lines.push(`max loss ${formatUsdAmount(Math.abs(maxLossUsd))}`);
  }
  if (asOfUtc?.trim()) {
    lines.push(`as of ${formatTimestamp(asOfUtc)} UTC`);
  }
  return lines.length > 0 ? lines.join(" · ") : undefined;
}
