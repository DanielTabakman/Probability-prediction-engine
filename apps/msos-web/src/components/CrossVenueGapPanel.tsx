"use client";

import { useEffect, useState } from "react";

import {
  DEMO_CROSS_VENUE_RESEARCH,
  fetchCrossVenueResearchPayload,
  type CrossVenueResearchPayload,
} from "@/lib/crossVenueResearch";

type CrossVenueGapPanelProps = {
  live: boolean;
};

function archiveLine(payload: CrossVenueResearchPayload): string {
  const cv = payload.archives?.find((a) => a.id === "cross_venue_event_gap");
  if (!cv) return "Archive depth unknown";
  return `${cv.calendar_days ?? 0} / ${cv.min_calendar_days ?? 14} daily snapshots`;
}

export function CrossVenueGapPanel({ live }: CrossVenueGapPanelProps) {
  const [payload, setPayload] = useState<CrossVenueResearchPayload | null>(null);

  useEffect(() => {
    if (!live) {
      setPayload(DEMO_CROSS_VENUE_RESEARCH);
      return;
    }
    let cancelled = false;
    void fetchCrossVenueResearchPayload().then((data) => {
      if (!cancelled) setPayload(data ?? DEMO_CROSS_VENUE_RESEARCH);
    });
    return () => {
      cancelled = true;
    };
  }, [live]);

  const cv = payload?.cross_venue;
  const topGap = cv?.top_gap_pct;
  const tradeable = cv?.tradeability?.tradeable_count ?? 0;
  const backtestReady = cv?.backtest?.strategy_ready ?? false;

  return (
    <section className="cross-venue-research panel compact" aria-label="Cross-venue research summary">
      <div className="cross-venue-research-header">
        <h3>Polymarket vs options gaps</h3>
        <span className="cross-venue-research-badge">{live ? "Research" : "Sample"}</span>
      </div>
      <p className="micro cross-venue-research-note">
        PM ↔ Deribit implied P(BTC &gt; K). Screening and backtest only — not trade signals.
      </p>
      <div className="cross-venue-research-grid">
        <div className="cross-venue-research-cell">
          <div className="cross-venue-research-k">Archive</div>
          <div className="cross-venue-research-v">{payload ? archiveLine(payload) : "—"}</div>
        </div>
        <div className="cross-venue-research-cell">
          <div className="cross-venue-research-k">Top gap today</div>
          <div className="cross-venue-research-v">
            {typeof topGap === "number" ? `${topGap.toFixed(1)}%` : "—"}
          </div>
        </div>
        <div className="cross-venue-research-cell">
          <div className="cross-venue-research-k">Tradeable rows</div>
          <div className="cross-venue-research-v">{tradeable}</div>
        </div>
        <div className="cross-venue-research-cell">
          <div className="cross-venue-research-k">Backtest ready</div>
          <div className={`cross-venue-research-v ${backtestReady ? "teal" : "muted"}`.trim()}>
            {backtestReady ? "Yes" : "Not yet"}
          </div>
        </div>
      </div>
      <p className="micro cross-venue-research-footer">Research only — not order execution.</p>
    </section>
  );
}
