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

function deltaPct(value: number | null | undefined): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(1)} pp`;
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

function resultLabel(result: ResultSummary | RunResponse): string {
  if (result.status === "NO_DATA") return "NO USABLE WINDOW";
  return result.verdict?.label || result.status || "UNKNOWN";
}

function resultExplanation(result: ResultSummary | RunResponse): string {
  if (result.status === "NO_DATA") return "The required historical window was incomplete. This is a data result, not evidence for or against the hypothesis.";
  if (result.verdict?.label === "PASS") return "Detected levels reacted more often than controls and cleared the frozen evidence rule.";
  if (result.verdict?.label === "FAIL") return "Detected levels underperformed controls and cleared the frozen evidence rule.";
  if (result.verdict?.label === "INCONCLUSIVE") return "There was not enough qualifying evidence in this window for a PASS/FAIL call.";
  return result.verdict?.reason || "Saved deterministic research result.";
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
      const response = await fetch("/api/market-structure/experiments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: "prospective_holdout_v0" }),
      });
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
      <div className="panel-sub">NEXT SCIENTIFIC TEST · PROSPECTIVE HOLDOUT v0</div>
      <div className="row" style={{ alignItems: "flex-start", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
        <div style={{ maxWidth: "760px" }}>
          <h2 style={{ marginBottom: "0.35rem" }}>Run the untouched future-window test.</h2>
          <p style={{ marginBottom: "0.35rem" }}>
            We froze the detector at <strong>2026-08-15 18:20 UTC</strong>, before this four-hour future window completed. The window is now complete, so this is the cleanest check of the hypothesis so far.
          </p>
          <p className="panel-sub" style={{ marginBottom: "0.5rem" }}>
            Same detector. Same control construction. Same touch/reaction rules. No tuning after seeing the historical result. This is a research test, not a trading backtest, and it cannot place trades.
          </p>
        </div>
        <button className="btn primary" type="button" onClick={runExperiment} disabled={running}>
          {running ? "Running holdout…" : "Run prospective holdout v0"}
        </button>
      </div>

      {error ? <p style={{ marginTop: "0.75rem" }}><strong>Experiment unavailable:</strong> {error}</p> : null}

      {latest ? (
        <div className="panel compact" style={{ marginTop: "1rem" }}>
          <div className="row" style={{ alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
            <strong>Prospective holdout result</strong>
            <span className={`tiny-pill ${tone(latest.verdict?.label)}`.trim()}>{resultLabel(latest)}</span>
          </div>
          <p style={{ margin: "0.55rem 0" }}>{resultExplanation(latest)}</p>
          {latest.status !== "NO_DATA" ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.5rem", marginTop: "0.75rem" }}>
              <div className="panel compact"><div className="panel-sub">Detected levels</div><strong>{latestDetector?.reacted ?? "—"} reactions / {latestDetector?.touched ?? "—"} touches</strong><div className="panel-sub">{pct(latestDetector?.reaction_rate_given_touch)}</div></div>
              <div className="panel compact"><div className="panel-sub">Matched controls</div><strong>{latestBaseline?.reacted ?? "—"} reactions / {latestBaseline?.touched ?? "—"} touches</strong><div className="panel-sub">{pct(latestBaseline?.reaction_rate_given_touch)}</div></div>
              <div className="panel compact"><div className="panel-sub">Difference</div><strong>{deltaPct(latest.verdict?.reaction_rate_delta)}</strong></div>
              <div className="panel compact"><div className="panel-sub">Detector frozen at</div><strong>{when(latest.detect_at)}</strong></div>
            </div>
          ) : null}
          <details style={{ marginTop: "0.75rem" }}>
            <summary style={{ cursor: "pointer" }}>Result details</summary>
            <div className="panel-sub" style={{ marginTop: "0.45rem" }}>{latest.result_id || "unsaved"}</div>
            {latest.verdict?.reason ? <div className="panel-sub" style={{ marginTop: "0.25rem" }}>{latest.verdict.reason}</div> : null}
          </details>
        </div>
      ) : null}

      <div style={{ marginTop: "1rem" }}>
        <div className="panel-sub">RECENT SAVED FORWARD TESTS</div>
        <p className="panel-sub" style={{ margin: "0.25rem 0 0.6rem" }}>
          These are saved runs from the live research API. The historical 12-window batch is summarized above because it is one retrospective experiment made of many windows.
        </p>
        {loading ? <p>Loading…</p> : results.length === 0 ? <p className="panel-sub">No saved forward-test results yet.</p> : (
          <div style={{ display: "grid", gap: "0.5rem" }}>
            {results.map((result) => (
              <div key={result.result_id || `${result.source}-${result.detect_at}`} className="panel compact">
                <div className="row" style={{ justifyContent: "space-between", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
                  <div>
                    <strong>{result.source?.toUpperCase() || "MARKET"} · {resultLabel(result)}</strong>
                    <div className="panel-sub">Detector frozen {when(result.detect_at)}</div>
                  </div>
                  <div className="panel-sub" style={{ maxWidth: "520px" }}>{resultExplanation(result)}</div>
                </div>
                <details style={{ marginTop: "0.45rem" }}>
                  <summary style={{ cursor: "pointer" }}>Numbers & result ID</summary>
                  <div className="panel-sub" style={{ marginTop: "0.35rem" }}>
                    detected {pct(result.detector_summary?.reaction_rate_given_touch)} · control {pct(result.baseline_summary?.reaction_rate_given_touch)} · {result.result_id || "result"}
                  </div>
                </details>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
