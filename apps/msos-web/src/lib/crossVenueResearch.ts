/**
 * Cross-venue research summary — read-only boundary (PM vs options gaps).
 */

export const PPE_CROSS_VENUE_RESEARCH_API_URL = (
  process.env.NEXT_PUBLIC_PPE_CROSS_VENUE_RESEARCH_API_URL ??
  "/ppe-display-api/cross-venue-research.json"
).trim();

export type CrossVenueResearchPayload = {
  kind: "cross_venue_research_boundary" | "cross_venue_research_error";
  schema_version?: number;
  as_of_utc?: string;
  archives?: Array<{
    id?: string;
    label?: string;
    calendar_days?: number;
    min_calendar_days?: number;
    stale?: boolean;
    last_snapshot_utc?: string | null;
  }>;
  cross_venue?: {
    top_gap_pct?: number | null;
    scan_row_count?: number;
    backtest?: {
      resolved_count?: number;
      pending_count?: number;
      strategy_ready?: boolean;
    };
    tradeability?: {
      tradeable_count?: number;
      strategy_ready?: boolean;
    };
    tradeability_backtest?: {
      tradeable_resolved_count?: number;
      bl_beat_pm_rate?: number | null;
      strategy_ready?: boolean;
    };
  };
  error?: string;
};

export function isCrossVenueResearchPayload(value: unknown): value is CrossVenueResearchPayload {
  if (!value || typeof value !== "object") return false;
  const p = value as Partial<CrossVenueResearchPayload>;
  return p.kind === "cross_venue_research_boundary" || p.kind === "cross_venue_research_error";
}

export async function fetchCrossVenueResearchPayload(): Promise<CrossVenueResearchPayload | null> {
  try {
    const res = await fetch(PPE_CROSS_VENUE_RESEARCH_API_URL, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(30_000),
    });
    if (!res.ok) return null;
    const data: unknown = await res.json();
    return isCrossVenueResearchPayload(data) ? data : null;
  } catch {
    return null;
  }
}

export const DEMO_CROSS_VENUE_RESEARCH: CrossVenueResearchPayload = {
  kind: "cross_venue_research_boundary",
  schema_version: 1,
  cross_venue: {
    top_gap_pct: 12.5,
    scan_row_count: 3,
    backtest: { resolved_count: 0, pending_count: 5, strategy_ready: false },
    tradeability: { tradeable_count: 1, strategy_ready: true },
  },
  archives: [
    { id: "cross_venue_event_gap", label: "Cross-venue PM ↔ Deribit", calendar_days: 8, min_calendar_days: 14 },
  ],
};
