"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

type Exp001aStatus = {
  status?: string;
  detail?: string;
  latest_snapshot_id?: string | null;
  latest_snapshot_at?: string | null;
  latest_candidate_count?: number | null;
  candidate_count?: number | null;
  cadence_seconds?: number | null;
  summary?: unknown;
};

function fmtWhen(value: string | null | undefined): string {
  if (!value) return "—";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function ageLabel(value: string | null | undefined): string {
  if (!value) return "waiting for first snapshot";
  const ms = Date.now() - new Date(value).getTime();
  if (!Number.isFinite(ms)) return "snapshot recorded";
  const minutes = Math.max(0, Math.floor(ms / 60_000));
  if (minutes < 1) return "less than a minute ago";
  if (minutes === 1) return "1 minute ago";
  return `${minutes} minutes ago`;
}

function Cell({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="panel compact" style={{ minHeight: "96px" }}>
      <div className="panel-sub">{label}</div>
      <strong style={{ fontSize: "1.05rem" }}>{value}</strong>
      {detail ? <div className="panel-sub" style={{ marginTop: "0.25rem" }}>{detail}</div> : null}
    </div>
  );
}

export function ActiveExperimentStatus() {
  const [payload, setPayload] = useState<Exp001aStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const response = await fetch("/api/market-structure/exp001a/status", { cache: "no-store" });
      const body = (await response.json()) as Exp001aStatus;
      if (!response.ok) throw new Error(body.detail || `HTTP ${response.status}`);
      setPayload(body);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load EXP-001A runtime status.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 15_000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  const candidateCount = payload?.latest_candidate_count ?? payload?.candidate_count ?? null;
  const cadence = payload?.cadence_seconds ?? 900;
  const running = payload?.status === "OK";
  const evidenceState = useMemo(() => {
    if (!running) return "NOT VERIFIED";
    if (!payload?.latest_snapshot_id) return "STARTING";
    return "COLLECTING";
  }, [payload?.latest_snapshot_id, running]);

  return (
    <section className="panel" aria-label="Active EXP-001A experiment status">
      <div className="row" style={{ justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
        <div>
          <div className="panel-sub">ACTIVE EXPERIMENT · EXP-001A</div>
          <h2 style={{ margin: "0.15rem 0 0.25rem" }}>Frozen-zone forward validation</h2>
          <p className="panel-sub" style={{ margin: 0, maxWidth: "760px" }}>
            Detector V0 is frozen. The recorder takes a prospective snapshot every 15 minutes and waits for future prices before scoring it against matched fake levels.
          </p>
        </div>
        <div className="row" style={{ gap: "0.45rem", flexWrap: "wrap" }}>
          <span className={`tiny-pill ${running ? "" : "amber"}`}>{running ? "LIVE" : "CHECK RUNTIME"}</span>
          <span className="tiny-pill">NO TRADING</span>
          <button className="btn" type="button" onClick={() => void refresh()}>Refresh</button>
        </div>
      </div>

      {error ? (
        <div className="panel compact" style={{ marginTop: "0.7rem" }}>
          <strong>Runtime status unavailable.</strong>
          <div className="panel-sub" style={{ marginTop: "0.25rem" }}>{error}</div>
        </div>
      ) : loading ? (
        <p className="panel-sub" style={{ marginTop: "0.7rem" }}>Loading live experiment state…</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(175px, 1fr))", gap: "0.55rem", marginTop: "0.7rem" }}>
          <Cell label="STATE" value={evidenceState} detail={running ? "Recorder endpoint reports OK." : payload?.detail || "Runtime has not reported OK."} />
          <Cell label="LATEST SNAPSHOT" value={payload?.latest_snapshot_id ? "RECORDED" : "—"} detail={`${ageLabel(payload?.latest_snapshot_at)} · ${fmtWhen(payload?.latest_snapshot_at)}`} />
          <Cell label="CANDIDATES" value={candidateCount == null ? "—" : String(candidateCount)} detail="Frozen levels in the latest prospective snapshot." />
          <Cell label="CADENCE" value={`${Math.round(cadence / 60)} MIN`} detail="Fixed before outcomes; not shortened for testing." />
          <Cell label="FORWARD EVIDENCE" value={evidenceState === "COLLECTING" ? "MATURING" : "—"} detail="15m / 1h / 4h / 1d outcomes are scored only after their future windows exist." />
          <Cell label="DECISION" value="WAIT FOR EVIDENCE" detail="No strategy or Hummingbot promotion until the experiment earns it." />
        </div>
      )}
    </section>
  );
}
