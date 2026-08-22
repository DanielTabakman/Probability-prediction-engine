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

const PROSPECTIVE_RESULT_ID = "ndax-1786818000-d6f199ca8ba2";

function pct(value: number | null | undefined): string {
  return typeof value === "number" && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "—";
}

function when(value: number | null | undefined): string {
  return typeof value === "number" && Number.isFinite(value)
    ? new Date(value * 1000).toLocaleString()
    : "—";
}

function resultLabel(result: ResultSummary): string {
  if (result.status === "NO_DATA") return "NO USABLE WINDOW";
  return result.verdict?.label || result.status || "UNKNOWN";
}

function resultExplanation(result: ResultSummary): string {
  if (result.status === "NO_DATA") return "The required historical window was incomplete. This is a data result, not evidence for or against the hypothesis.";
  if (result.verdict?.label === "PASS") return "Detected levels reacted more often than controls and cleared the frozen evidence rule.";
  if (result.verdict?.label === "FAIL") return "Detected levels underperformed controls and cleared the frozen evidence rule.";
  if (result.verdict?.label === "INCONCLUSIVE") return "This single four-hour window did not contain enough qualifying touches for a PASS/FAIL call.";
  return result.verdict?.reason || "Saved deterministic research result.";
}

export function ResearchExperimentPanel() {
  const [results, setResults] = useState<ResultSummary[]>([]);
  const [loading, setLoading] = useState(true);
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

  const prospective = results.find((result) => result.result_id === PROSPECTIVE_RESULT_ID);

  return (
    <section className="panel">
      <div className="panel-sub">V0 TESTING · COMPLETE</div>
      <h2 style={{ marginBottom: "0.35rem" }}>We are not running more v0 tests from this page.</h2>
      <p style={{ maxWidth: "900px", marginBottom: "0.35rem" }}>
        The clean prospective holdout and the larger untouched historical batch are complete. The larger batch did not demonstrate an edge, so repeatedly rerunning or tweaking v0 would turn research into result-chasing.
      </p>
      <p className="panel-sub" style={{ marginBottom: "0.8rem" }}>
        If the project continues, the next experiment should begin with a new written v1 hypothesis and frozen rules before another sample is inspected. This page remains useful for reviewing saved v0 evidence.
      </p>

      <div className="panel compact">
        <div className="panel-sub">CLEAN PROSPECTIVE HOLDOUT · AUGUST 15</div>
        {error ? <p><strong>Saved-result history unavailable:</strong> {error}</p> : loading ? <p>Loading saved result…</p> : prospective ? (
          <>
            <div className="row" style={{ alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
              <strong>{resultLabel(prospective)}</strong>
              <span className="tiny-pill amber">0 detector touches · 0 control touches</span>
            </div>
            <p style={{ margin: "0.55rem 0 0" }}>
              The future window was valid and completed after the detector was frozen, but neither arm was touched. That makes this holdout underpowered rather than positive or negative evidence.
            </p>
            <details style={{ marginTop: "0.65rem" }}>
              <summary style={{ cursor: "pointer" }}>Holdout details</summary>
              <div className="panel-sub" style={{ marginTop: "0.4rem" }}>
                Detector frozen {when(prospective.detect_at)} · detected {pct(prospective.detector_summary?.reaction_rate_given_touch)} · control {pct(prospective.baseline_summary?.reaction_rate_given_touch)} · {prospective.result_id}
              </div>
            </details>
          </>
        ) : (
          <p style={{ marginBottom: 0 }}>The known holdout result is not in the latest API page. Result ID: <code>{PROSPECTIVE_RESULT_ID}</code>.</p>
        )}
      </div>

      <details style={{ marginTop: "1rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 700 }}>Recent saved forward-test history</summary>
        <p className="panel-sub" style={{ margin: "0.5rem 0" }}>
          These are individual saved four-hour runs. They are supporting history; the 168-window batch shown above is the primary v0 evidence.
        </p>
        {loading ? <p>Loading…</p> : results.length === 0 ? <p className="panel-sub">No saved forward-test results available.</p> : (
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
      </details>
    </section>
  );
}
