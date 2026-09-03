"use client";

import { useMemo, useState } from "react";
import { SANDBOX_ROWS } from "@/data/marketStructureSandboxData";

const START_EPOCH = 1784332800;
const ANCHOR_SECONDS = 14_400;
const SCALE_BITS: Record<string, number> = { "15m": 2, "1h": 4, "4h": 8, "1d": 16 };
const KIND_LABELS: Record<number, string> = { 1: "support", 2: "resistance", 3: "mixed" };

type RawSummary = {
  levels?: number;
  touched?: number;
  successes?: number;
  success_rate_given_touch?: number | null;
  rejections?: number;
  breakouts?: number;
  continuations?: number;
  whipsaws?: number;
};

type RawPathPoint = { t: number; p: number; signed_distance_bps: number };
type RawLevel = {
  center: number;
  touched: boolean;
  touch_time?: number | null;
  touch_price?: number | null;
  touch_distance_bps?: number | null;
  approach_price?: number | null;
  pre_touch_side?: string | null;
  reaction?: boolean;
  rejection?: boolean;
  breakout?: boolean;
  continuation?: boolean;
  whipsaw?: boolean;
  success?: boolean;
  persistence?: number;
  scales?: string[];
  kind?: string;
  rejection_excursion_bps?: number;
  breakout_excursion_bps?: number;
  max_move_away_bps?: number;
  final_signed_distance_bps?: number | null;
  path?: RawPathPoint[];
};

type RawAnchor = {
  status?: string;
  detect_at?: number;
  detector?: { summary?: RawSummary; levels?: RawLevel[] };
  baseline?: { summary?: RawSummary; levels?: RawLevel[] };
};

type RawReplay = {
  status?: string;
  replay_version?: string;
  scientific_label?: string;
  canonical_research_effect?: boolean;
  parameters?: Record<string, unknown>;
  aggregate?: {
    detector?: RawSummary;
    baseline?: RawSummary;
    success_rate_delta?: number | null;
    anchors_total?: number;
    anchors_ok?: number;
  };
  anchors?: RawAnchor[];
  research_note?: string;
  detail?: string;
};

function pct(value: number | null | undefined) {
  return typeof value === "number" && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "—";
}

function signedPp(value: number | null | undefined) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  const points = value * 100;
  return `${points > 0 ? "+" : ""}${points.toFixed(1)} pp`;
}

function anchorSeconds(index: number) {
  return START_EPOCH + index * ANCHOR_SECONDS;
}

function anchorDate(index: number) {
  return new Date(anchorSeconds(index) * 1000);
}

function formatDate(index: number) {
  return anchorDate(index).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric" });
}

function formatTimestamp(value: number | null | undefined) {
  return typeof value === "number" && Number.isFinite(value)
    ? new Date(value * 1000).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })
    : "—";
}

function rate(success: number, touched: number) {
  return touched > 0 ? success / touched : null;
}

function Control({ label, children, note }: { label: string; children: React.ReactNode; note?: string }) {
  return <label className="panel compact" style={{ display: "grid", gap: "0.4rem" }}>
    <span className="panel-sub">{label}</span>
    {children}
    {note ? <span className="panel-sub">{note}</span> : null}
  </label>;
}

function RawPathChart({ level }: { level: RawLevel }) {
  const path = Array.isArray(level.path) ? level.path : [];
  if (!path.length) return <p className="panel-sub">No path points returned for this event.</p>;

  const width = 880;
  const height = 280;
  const pad = 36;
  const values = path.map((point) => point.signed_distance_bps);
  const magnitude = Math.max(10, ...values.map((value) => Math.abs(value)));
  const x = (index: number) => pad + (index / Math.max(1, path.length - 1)) * (width - pad * 2);
  const y = (value: number) => height / 2 - (value / magnitude) * (height / 2 - pad);
  const zeroY = y(0);

  return <div className="panel compact" style={{ overflowX: "auto" }}>
    <div className="row" style={{ justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
      <div>
        <div className="panel-sub">ACTUAL PRICE PATH AROUND TOUCH</div>
        <strong>{level.center.toFixed(3)} CAD · approached from {level.pre_touch_side ?? "—"}</strong>
      </div>
      <div className="panel-sub">touch {formatTimestamp(level.touch_time)} · {level.touch_distance_bps?.toFixed(1) ?? "—"} bps from level</div>
    </div>
    <svg role="img" aria-label="Raw price path around touched level" viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", minWidth: "680px", marginTop: "0.5rem" }}>
      <line x1={pad} x2={width - pad} y1={zeroY} y2={zeroY} stroke="currentColor" strokeDasharray="6 5" opacity="0.45" />
      <text x={pad + 4} y={zeroY - 7} fill="currentColor" fontSize="11">price level</text>
      <polyline
        points={path.map((point, index) => `${x(index)},${y(point.signed_distance_bps)}`).join(" ")}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      />
      {path.map((point, index) => <circle key={`${point.t}-${index}`} cx={x(index)} cy={y(point.signed_distance_bps)} r="2.3" fill="currentColor">
        <title>{`${formatTimestamp(point.t)} · ${point.p.toFixed(3)} · ${point.signed_distance_bps.toFixed(1)} bps from level`}</title>
      </circle>)}
    </svg>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.5rem" }}>
      <div className="panel compact"><div className="panel-sub">Rejection</div><strong>{level.rejection ? "YES" : "NO"}</strong><div className="panel-sub">{level.rejection_excursion_bps?.toFixed(1) ?? "—"} bps back toward approach side</div></div>
      <div className="panel compact"><div className="panel-sub">Breakout</div><strong>{level.breakout ? "YES" : "NO"}</strong><div className="panel-sub">{level.breakout_excursion_bps?.toFixed(1) ?? "—"} bps through level</div></div>
      <div className="panel compact"><div className="panel-sub">Continuation</div><strong>{level.continuation ? "YES" : "NO"}</strong><div className="panel-sub">still beyond threshold at horizon end</div></div>
      <div className="panel compact"><div className="panel-sub">Whipsaw</div><strong>{level.whipsaw ? "YES" : "NO"}</strong><div className="panel-sub">both rejection and breakout occurred</div></div>
    </div>
  </div>;
}

export function MarketStructureSandbox() {
  const [minPersistence, setMinPersistence] = useState(2);
  const [scale, setScale] = useState("all");
  const [kind, setKind] = useState("all");
  const [outcomeBps, setOutcomeBps] = useState(25);
  const [startAnchor, setStartAnchor] = useState(0);
  const [endAnchor, setEndAnchor] = useState(167);
  const [touchBps, setTouchBps] = useState(10);
  const [outcomeHorizonMinutes, setOutcomeHorizonMinutes] = useState(30);
  const [forwardHours, setForwardHours] = useState(4);
  const [outcomeMode, setOutcomeMode] = useState("reaction");
  const [rawReplay, setRawReplay] = useState<RawReplay | null>(null);
  const [rawLoading, setRawLoading] = useState(false);
  const [rawError, setRawError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const filtered = useMemo(() => SANDBOX_ROWS.filter((row) => {
    const [anchor, , , persistence, scaleMask, kindCode] = row;
    if (anchor < startAnchor || anchor > endAnchor) return false;
    if (persistence < minPersistence) return false;
    if (scale !== "all" && (scaleMask & SCALE_BITS[scale]) === 0) return false;
    if (kind !== "all" && KIND_LABELS[kindCode] !== kind) return false;
    return true;
  }), [endAnchor, kind, minPersistence, scale, startAnchor]);

  const artifactStats = useMemo(() => {
    let detTouched = 0, detSuccess = 0, baseTouched = 0, baseSuccess = 0;
    for (const row of filtered) {
      if (row[6] === 1) {
        detTouched += 1;
        if (row[7] >= outcomeBps) detSuccess += 1;
      }
      if (row[8] === 1) {
        baseTouched += 1;
        if (row[9] >= outcomeBps) baseSuccess += 1;
      }
    }
    const detRate = rate(detSuccess, detTouched);
    const baseRate = rate(baseSuccess, baseTouched);
    return {
      detTouched, detSuccess, baseTouched, baseSuccess, detRate, baseRate,
      delta: detRate === null || baseRate === null ? null : detRate - baseRate,
    };
  }, [filtered, outcomeBps]);

  const touchedRows = useMemo(() => filtered.filter((row) => row[6] === 1), [filtered]);
  const chartRows = touchedRows.slice(0, 450);
  const chartWidth = 880;
  const chartHeight = 270;
  const pad = 34;
  const yMax = Math.max(50, Math.min(250, ...chartRows.map((row) => row[7]), outcomeBps * 1.4));
  const span = Math.max(1, endAnchor - startAnchor);
  const x = (anchor: number) => pad + ((anchor - startAnchor) / span) * (chartWidth - pad * 2);
  const y = (move: number) => chartHeight - pad - (Math.min(move, yMax) / yMax) * (chartHeight - pad * 2);
  const thresholdY = y(outcomeBps);

  const rawExample = useMemo(() => {
    for (const anchor of rawReplay?.anchors ?? []) {
      const level = anchor.detector?.levels?.find((candidate) => candidate.touched && (candidate.path?.length ?? 0) > 0);
      if (level) return level;
    }
    return null;
  }, [rawReplay]);

  const reset = () => {
    setMinPersistence(2);
    setScale("all");
    setKind("all");
    setOutcomeBps(25);
    setStartAnchor(0);
    setEndAnchor(167);
    setTouchBps(10);
    setOutcomeHorizonMinutes(30);
    setForwardHours(4);
    setOutcomeMode("reaction");
    setRawReplay(null);
    setRawError(null);
  };

  const runRawReplay = async () => {
    setRawLoading(true);
    setRawError(null);
    try {
      const response = await fetch("/api/market-structure/sandbox-replay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "ndax",
          anchor_start_at: anchorSeconds(startAnchor),
          anchor_end_at: anchorSeconds(endAnchor),
          anchor_step_seconds: ANCHOR_SECONDS,
          forward_seconds: forwardHours * 3_600,
          min_persistence: minPersistence,
          required_scales: scale === "all" ? [] : [scale],
          kind,
          touch_bps: touchBps,
          outcome_bps: outcomeBps,
          outcome_horizon_seconds: outcomeHorizonMinutes * 60,
          outcome_mode: outcomeMode,
          max_path_points: 100,
        }),
      });
      const payload = (await response.json()) as RawReplay;
      if (!response.ok) throw new Error(payload.detail || `HTTP ${response.status}`);
      setRawReplay(payload);
    } catch (error) {
      setRawReplay(null);
      setRawError(error instanceof Error ? error.message : "Raw replay is unavailable.");
    } finally {
      setRawLoading(false);
    }
  };

  const copyHypothesis = async () => {
    const text = [
      "Market Structure Sandbox candidate hypothesis",
      `sample: ${formatDate(startAnchor)} → ${formatDate(endAnchor)}`,
      `minimum persistence: ${minPersistence} scales`,
      `required scale: ${scale}`,
      `level kind: ${kind}`,
      `outcome: ${outcomeMode}`,
      `outcome threshold: ${outcomeBps} bps`,
      `touch threshold: ${touchBps} bps`,
      `outcome horizon: ${outcomeHorizonMinutes} minutes after first touch`,
      `forward observation window: ${forwardHours} hours`,
      "IMPORTANT: exploratory only. Freeze these rules before testing a fresh evaluation sample.",
    ].join("\n");
    await navigator.clipboard?.writeText(text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };

  const detectorRaw = rawReplay?.aggregate?.detector;
  const baselineRaw = rawReplay?.aggregate?.baseline;

  return (
    <section className="panel">
      <div className="row" style={{ alignItems: "center", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
        <div>
          <div className="panel-sub">SANDBOX · EXPLORATORY ONLY · V0 STAYS LOCKED</div>
          <h2 style={{ margin: "0.2rem 0 0.35rem" }}>Move the dials, then replay the actual price paths.</h2>
        </div>
        <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap" }}>
          <button type="button" className="btn" onClick={reset}>Reset to V0</button>
          <button type="button" className="btn" onClick={copyHypothesis}>{copied ? "Copied" : "Copy candidate hypothesis"}</button>
          <button type="button" className="btn" disabled={rawLoading} onClick={() => void runRawReplay()}>{rawLoading ? "Replaying…" : "Replay raw paths"}</button>
        </div>
      </div>
      <p style={{ maxWidth: "1000px", marginTop: 0 }}>
        The instant view below re-filters the frozen V0 event artifact. The raw replay button asks the engine to recompute first touches and post-touch paths from historical observations, which is what makes touch distance, horizon, rejection, breakout and continuation real research controls instead of guesses.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "0.65rem" }}>
        <Control label="Minimum persistence" note="How many timeframes must agree on the level.">
          <input aria-label="Minimum persistence" type="range" min={2} max={4} step={1} value={minPersistence} onChange={(event) => setMinPersistence(Number(event.target.value))} />
          <strong>{minPersistence}+ timeframes</strong>
        </Control>
        <Control label="Must appear on timeframe">
          <select value={scale} onChange={(event) => setScale(event.target.value)}>
            <option value="all">Any timeframe mix</option><option value="15m">15m</option><option value="1h">1h</option><option value="4h">4h</option><option value="1d">1d</option>
          </select>
        </Control>
        <Control label="Level type">
          <select value={kind} onChange={(event) => setKind(event.target.value)}>
            <option value="all">All kinds</option><option value="support">Support</option><option value="resistance">Resistance</option><option value="mixed">Mixed</option>
          </select>
        </Control>
        <Control label="Outcome" note="This replaces the misleading assumption that every failed bounce is an opposite trade.">
          <select value={outcomeMode} onChange={(event) => setOutcomeMode(event.target.value)}>
            <option value="reaction">Any move away</option>
            <option value="rejection">Reject back to approach side</option>
            <option value="breakout">Break through the level</option>
            <option value="continuation">Break and remain through it</option>
          </select>
        </Control>
        <Control label="Outcome size">
          <input aria-label="Outcome threshold" type="range" min={5} max={150} step={5} value={outcomeBps} onChange={(event) => setOutcomeBps(Number(event.target.value))} />
          <strong>{outcomeBps} bps · {(outcomeBps / 100).toFixed(2)}%</strong>
        </Control>
        <Control label="Touch distance" note="How close price must get before the level counts as touched.">
          <input aria-label="Touch threshold" type="range" min={2} max={50} step={2} value={touchBps} onChange={(event) => setTouchBps(Number(event.target.value))} />
          <strong>{touchBps} bps</strong>
        </Control>
        <Control label="Outcome horizon" note="How long after first touch we watch the path.">
          <select value={outcomeHorizonMinutes} onChange={(event) => setOutcomeHorizonMinutes(Number(event.target.value))}>
            {[15, 30, 60, 120, 240].filter((minutes) => minutes <= forwardHours * 60).map((minutes) => <option key={minutes} value={minutes}>{minutes < 60 ? `${minutes}m` : `${minutes / 60}h`}</option>)}
          </select>
        </Control>
        <Control label="Forward window" note="Maximum historical path available after each frozen detection time.">
          <select value={forwardHours} onChange={(event) => {
            const next = Number(event.target.value);
            setForwardHours(next);
            setOutcomeHorizonMinutes((current) => Math.min(current, next * 60));
          }}>
            <option value={1}>1h</option><option value={4}>4h</option><option value={12}>12h</option><option value={24}>24h</option>
          </select>
        </Control>
      </div>

      <div className="panel compact" style={{ marginTop: "0.75rem" }}>
        <div className="panel-sub">SAMPLE WINDOW</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem", alignItems: "end" }}>
          <label><span className="panel-sub">Start · {formatDate(startAnchor)}</span><input style={{ width: "100%" }} type="range" min={0} max={166} value={startAnchor} onChange={(event) => setStartAnchor(Math.min(Number(event.target.value), endAnchor - 1))} /></label>
          <label><span className="panel-sub">End · {formatDate(endAnchor)}</span><input style={{ width: "100%" }} type="range" min={1} max={167} value={endAnchor} onChange={(event) => setEndAnchor(Math.max(Number(event.target.value), startAnchor + 1))} /></label>
        </div>
      </div>

      <div className="panel compact" style={{ marginTop: "0.8rem" }}>
        <div className="panel-sub">INSTANT ARTIFACT LENS · V0 REACTION METRIC ONLY</div>
        <p className="panel-sub" style={{ margin: "0.25rem 0 0.65rem" }}>
          This responds instantly because it uses the saved V0 event summaries. It can vary filters and outcome magnitude, but it cannot honestly distinguish rejection from breakout or recompute touch/horizon rules.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(175px, 1fr))", gap: "0.55rem" }}>
          <div className="panel compact"><div className="panel-sub">Detected levels</div><strong>{artifactStats.detSuccess} / {artifactStats.detTouched}</strong><div className="panel-sub">{pct(artifactStats.detRate)} reaction rate</div></div>
          <div className="panel compact"><div className="panel-sub">Matched controls</div><strong>{artifactStats.baseSuccess} / {artifactStats.baseTouched}</strong><div className="panel-sub">{pct(artifactStats.baseRate)} reaction rate</div></div>
          <div className="panel compact"><div className="panel-sub">Difference</div><strong>{signedPp(artifactStats.delta)}</strong><div className="panel-sub">detector minus control</div></div>
          <div className="panel compact"><div className="panel-sub">Filtered candidate pairs</div><strong>{filtered.length}</strong><div className="panel-sub">from 225 frozen detector/control pairs</div></div>
        </div>
      </div>

      <div className="panel compact" style={{ marginTop: "0.8rem", overflowX: "auto" }}>
        <div className="row" style={{ justifyContent: "space-between", gap: "0.7rem", flexWrap: "wrap" }}>
          <div><div className="panel-sub">FROZEN EVENT VIEW · MAX MOVE AWAY AFTER TOUCH</div><strong>Useful for threshold intuition; not enough for directionality.</strong></div>
          <div className="panel-sub">circle = detector · faint square = matched control · line = current threshold</div>
        </div>
        {chartRows.length ? <svg role="img" aria-label="Historical touched level outcomes" viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: "100%", minWidth: "680px", marginTop: "0.5rem" }}>
          <line x1={pad} x2={chartWidth - pad} y1={thresholdY} y2={thresholdY} stroke="currentColor" strokeDasharray="6 5" opacity="0.55" />
          <text x={pad + 4} y={Math.max(14, thresholdY - 6)} fill="currentColor" fontSize="11">{outcomeBps} bps threshold</text>
          {chartRows.map((row, index) => {
            const detectorSuccess = row[7] >= outcomeBps;
            const baseSuccess = row[9] >= outcomeBps;
            const px = x(row[0]);
            return <g key={`${row[0]}-${row[2]}-${index}`}>
              {row[8] === 1 ? <rect x={px - 3} y={y(row[9]) - 3} width="6" height="6" fill="currentColor" opacity={baseSuccess ? 0.32 : 0.12} /> : null}
              <circle cx={px} cy={y(row[7])} r={detectorSuccess ? 4 : 2.7} fill="currentColor" opacity={detectorSuccess ? 0.9 : 0.35}><title>{`${formatDate(row[0])} · level ${row[2]} · move ${row[7]} bps · persistence ${row[3]}`}</title></circle>
            </g>;
          })}
          <line x1={pad} x2={chartWidth - pad} y1={chartHeight - pad} y2={chartHeight - pad} stroke="currentColor" opacity="0.25" />
          <text x={pad} y={chartHeight - 8} fill="currentColor" fontSize="11">{formatDate(startAnchor)}</text>
          <text x={chartWidth - pad - 86} y={chartHeight - 8} fill="currentColor" fontSize="11">{formatDate(endAnchor)}</text>
        </svg> : <p className="panel-sub">No touched detector events match these filters.</p>}
      </div>

      <div className="panel" style={{ marginTop: "0.9rem" }}>
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          <div>
            <div className="panel-sub">RAW REPLAY · ACTUAL PATH CLASSIFICATION</div>
            <h3 style={{ margin: "0.2rem 0" }}>Recompute these settings from the historical price path.</h3>
          </div>
          <button type="button" className="btn" disabled={rawLoading} onClick={() => void runRawReplay()}>{rawLoading ? "Replaying…" : "Replay these settings"}</button>
        </div>
        <p className="panel-sub" style={{ marginTop: "0.25rem" }}>
          This is the slower, scientifically honest path. It recomputes first touches under the selected distance, watches the selected horizon, and separates rejection from breakout and continuation.
        </p>

        {rawError ? <div className="panel compact">
          <strong>Raw replay is not available from the deployed engine yet.</strong>
          <div className="panel-sub" style={{ marginTop: "0.35rem" }}>{rawError} The instant frozen-artifact lens above still works.</div>
        </div> : null}

        {rawReplay ? <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: "0.55rem" }}>
            <div className="panel compact"><div className="panel-sub">Detector · {outcomeMode}</div><strong>{detectorRaw?.successes ?? 0} / {detectorRaw?.touched ?? 0}</strong><div className="panel-sub">{pct(detectorRaw?.success_rate_given_touch)} success rate</div></div>
            <div className="panel compact"><div className="panel-sub">Matched controls</div><strong>{baselineRaw?.successes ?? 0} / {baselineRaw?.touched ?? 0}</strong><div className="panel-sub">{pct(baselineRaw?.success_rate_given_touch)} success rate</div></div>
            <div className="panel compact"><div className="panel-sub">Difference</div><strong>{signedPp(rawReplay.aggregate?.success_rate_delta)}</strong><div className="panel-sub">detector minus control</div></div>
            <div className="panel compact"><div className="panel-sub">Whipsaws</div><strong>{detectorRaw?.whipsaws ?? 0}</strong><div className="panel-sub">touched detector levels moved materially both ways</div></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: "0.55rem", marginTop: "0.55rem" }}>
            <div className="panel compact"><div className="panel-sub">All rejections</div><strong>{detectorRaw?.rejections ?? 0}</strong></div>
            <div className="panel compact"><div className="panel-sub">All breakouts</div><strong>{detectorRaw?.breakouts ?? 0}</strong></div>
            <div className="panel compact"><div className="panel-sub">All continuations</div><strong>{detectorRaw?.continuations ?? 0}</strong></div>
            <div className="panel compact"><div className="panel-sub">Anchors replayed</div><strong>{rawReplay.aggregate?.anchors_ok ?? 0} / {rawReplay.aggregate?.anchors_total ?? 0}</strong></div>
          </div>
          {rawExample ? <div style={{ marginTop: "0.7rem" }}><RawPathChart level={rawExample} /></div> : <p className="panel-sub">No touched detector event with a path matched these settings.</p>}
          <p className="panel-sub" style={{ marginBottom: 0, marginTop: "0.65rem" }}>
            <strong>Exploratory only:</strong> {rawReplay.research_note ?? "A result discovered by moving these dials is not validated until the configuration is frozen and tested on fresh data."}
          </p>
        </> : null}
      </div>

      <details style={{ marginTop: "0.9rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 700 }}>Show example frozen V0 events under the current filters</summary>
        <div style={{ display: "grid", gap: "0.45rem", marginTop: "0.55rem" }}>
          {filtered.slice(0, 12).map((row, index) => <div key={`${row[0]}-${row[2]}-detail-${index}`} className="panel compact">
            <strong>{formatDate(row[0])} · {row[2].toFixed(3)} CAD</strong>
            <div className="panel-sub">last price {row[1].toFixed(3)} · persistence {row[3]} · {KIND_LABELS[row[5]] ?? "unknown"} · detector {row[6] ? `${row[7].toFixed(1)} bps max move` : "not touched"} · control {row[8] ? `${row[9].toFixed(1)} bps` : "not touched"}</div>
          </div>)}
        </div>
      </details>
    </section>
  );
}
