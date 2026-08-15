"use client";

import { useCallback, useEffect, useState } from "react";

type SummaryStats = {
  levels?: number | null;
  touched?: number | null;
  reacted?: number | null;
  reaction_rate_given_touch?: number | null;
};

type Verdict = {
  label?: string | null;
  reason?: string | null;
  reaction_rate_delta?: number | null;
};

type ResultSummary = {
  result_id?: string | null;
  saved_at?: string | null;
  status?: string | null;
  source?: string | null;
  detect_at?: number | null;
  forward_end_at?: number | null;
  verdict?: Verdict | null;
  detector_summary?: SummaryStats | null;
  baseline_summary?: SummaryStats | null;
};

type ListResponse = {
  status?: string;
  detail?: string;
  results?: ResultSummary[];
};

type RunResponse = ResultSummary & {
  detail?: string;
  verdict?: Verdict | null;
  detector?: { summary?: SummaryStats | null } | null;
  baseline?: { summary?: SummaryStats | null } | null;
};

function pct(value: number | null | undefined): string {
  return typeof value === "number" && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "—";
}

function when(value: number | null | undefined): string {
  return typeof value === "number" && Number.isFinite(value)
    ? new Date(value * 1000).toLocaleString()
    : "—";
}

function tone(label: string | null | undefined): string {
  if (label === "PASS") return "teal";
  if (label === "FAIL") return "red";
  return "amber";
}

export function ResearchExperimentPanel() {
  const [results, setResults] = useState<ResultSummary[]>([]);
  const [latest, setLatest] = useState<RunResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const response = await fetch("/api/market-structure/experiments", { cache: "no-store" });
      const payload = (await response.json()) as ListResponse;
      if (!response.ok) throw new Error(payload.detail || `HTTP ${response.status}`);
      setResults(Array.isArray(payload.results) ? payload.results : []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load experiment history.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function runExperiment() {
    setRunning(true);
    setError(null);
    try {
      const response = await fetch("/api/market-structure/experiments", { method: "POST" });
      const payload = (await response.json()) as RunResponse;
      if (!response.ok) throw new Error(payload.detail || `HTTP ${response.status}`);
      setLatest(payload);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Experiment failed.");
    } finally {
      setRunning(false);
    }
  }

  const latestDetector = latest?.detector?.summary ?? latest?.detector_summary;
  const latestBaseline = latest?.baseline?.summary ?? latest?.baseline_summary;

  return (
    <section className="panel">
      <div className="panel-sub">CURRENT EXPERIMENT · DETERMINISTIC</div>
      <div className="row" style={{ alignItems: "flex-start", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div style={{ maxWidth: "760px" }}>
          <h2 style={{ marginBottom: "0.35rem" }}>Do persistent multi-scale levels predict future reactions?</h2>
          <p className="panel-sub" style={{ marginBottom: "0.5rem" }}>
            Freeze the detector four hours in the past, observe the next four hours, and compare detected levels with matched control levels. This tests information, not trading profitability.
          </p>
        </div>
        <button className="btn primary" type="button" onClick={runExperiment} disabled={running}>
          {running ? "Running…" : "Run current experiment"}
        </button>
      </div>

      {error ? <p style={{ marginTop: "0.75rem" }}><strong>Experiment unavailable:</strong> {error}</p> : null}

      {latest ? (
        <div className="panel compact" style={{ marginTop: "1rem" }}>
          <div className="row" style={{ alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
            <strong>Latest run</strong>
            <span className={`tiny-pill ${tone(latest.verdict?.label)}`.trim()}>{latest.verdict?.label || latest.status || "UNKNOWN"}</span>
            <span className="panel-sub">{latest.result_id || "unsaved"}</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.5rem", marginTop: "0.75rem" }}>
            <div className="panel compact"><div className="panel-sub">Detected reaction rate</div><strong>{pct(latestDetector?.reaction_rate_given_touch)}</strong></div>
            <div className="panel compact"><div className="panel-sub">Control reaction rate</div><strong>{pct(latestBaseline?.reaction_rate_given_touch)}</strong></div>
            <div className="panel compact"><div className="panel-sub">Difference</div><strong>{pct(latest.verdict?.reaction_rate_delta)}</strong></div>
            <div className="panel compact"><div className="panel-sub">Detection time</div><strong>{when(latest.detect_at)}</strong></div>
          </div>
          {latest.verdict?.reason ? <p className="panel-sub" style={{ marginTop: "0.75rem", marginBottom: 0 }}>{latest.verdict.reason}</p> : null}
        </div>
      ) : null}

      <div style={{ marginTop: "1rem" }}>
        <div className="panel-sub">RECENT SAVED RESULTS</div>
        {loading ? <p>Loading…</p> : results.length === 0 ? <p className="panel-sub">No saved experiment results yet.</p> : (
          <div style={{ display: "grid", gap: "0.5rem" }}>
            {results.map((result) => (
              <div key={result.result_id || `${result.source}-${result.detect_at}`} className="panel compact">
                <div className="row" style={{ justifyContent: "space-between", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
                  <div>
                    <strong>{result.source?.toUpperCase() || "MARKET"}</strong>
                    <div className="panel-sub">{when(result.detect_at)} · {result.result_id || "result"}</div>
                  </div>
                  <span className={`tiny-pill ${tone(result.verdict?.label)}`.trim()}>{result.verdict?.label || result.status || "UNKNOWN"}</span>
                  <div className="panel-sub">detected {pct(result.detector_summary?.reaction_rate_given_touch)} · control {pct(result.baseline_summary?.reaction_rate_given_touch)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
