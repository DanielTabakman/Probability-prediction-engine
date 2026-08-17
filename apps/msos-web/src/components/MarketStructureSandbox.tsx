"use client";

import { useMemo, useState } from "react";
import { SANDBOX_ROWS } from "@/data/marketStructureSandboxData";

const START_EPOCH = 1784332800;
const ANCHOR_SECONDS = 14_400;
const V0_TOUCH_BPS = 10;
const V0_REACTION_WINDOW_MINUTES = 30;
const V0_FORWARD_HOURS = 4;

const SCALE_BITS: Record<string, number> = { "15m": 2, "1h": 4, "4h": 8, "1d": 16 };
const KIND_LABELS: Record<number, string> = { 1: "support", 2: "resistance", 3: "mixed" };

function pct(value: number | null) {
  return value === null ? "—" : `${(value * 100).toFixed(1)}%`;
}

function signedPp(value: number | null) {
  if (value === null) return "—";
  const points = value * 100;
  return `${points > 0 ? "+" : ""}${points.toFixed(1)} pp`;
}

function anchorDate(index: number) {
  return new Date((START_EPOCH + index * ANCHOR_SECONDS) * 1000);
}

function formatDate(index: number) {
  return anchorDate(index).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric" });
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

export function MarketStructureSandbox() {
  const [minPersistence, setMinPersistence] = useState(2);
  const [scale, setScale] = useState("all");
  const [kind, setKind] = useState("all");
  const [reactionBps, setReactionBps] = useState(25);
  const [startAnchor, setStartAnchor] = useState(0);
  const [endAnchor, setEndAnchor] = useState(167);
  const [inverse, setInverse] = useState(false);
  const [copied, setCopied] = useState(false);

  const filtered = useMemo(() => SANDBOX_ROWS.filter((row) => {
    const [anchor, , , persistence, scaleMask, kindCode] = row;
    if (anchor < startAnchor || anchor > endAnchor) return false;
    if (persistence < minPersistence) return false;
    if (scale !== "all" && (scaleMask & SCALE_BITS[scale]) === 0) return false;
    if (kind !== "all" && KIND_LABELS[kindCode] !== kind) return false;
    return true;
  }), [endAnchor, kind, minPersistence, scale, startAnchor]);

  const stats = useMemo(() => {
    let detTouched = 0, detSuccess = 0, baseTouched = 0, baseSuccess = 0;
    for (const row of filtered) {
      const detWasTouched = row[6] === 1;
      const detReacted = row[7] >= reactionBps;
      const baseWasTouched = row[8] === 1;
      const baseReacted = row[9] >= reactionBps;
      if (detWasTouched) { detTouched += 1; if (inverse ? !detReacted : detReacted) detSuccess += 1; }
      if (baseWasTouched) { baseTouched += 1; if (inverse ? !baseReacted : baseReacted) baseSuccess += 1; }
    }
    const detRate = rate(detSuccess, detTouched);
    const baseRate = rate(baseSuccess, baseTouched);
    return {
      detTouched, detSuccess, baseTouched, baseSuccess, detRate, baseRate,
      delta: detRate === null || baseRate === null ? null : detRate - baseRate,
    };
  }, [filtered, inverse, reactionBps]);

  const touchedRows = useMemo(() => filtered.filter((row) => row[6] === 1), [filtered]);
  const chartRows = touchedRows.slice(0, 450);
  const chartWidth = 880;
  const chartHeight = 270;
  const pad = 34;
  const yMax = Math.max(50, Math.min(250, ...chartRows.map((row) => row[7]), reactionBps * 1.4));
  const span = Math.max(1, endAnchor - startAnchor);
  const x = (anchor: number) => pad + ((anchor - startAnchor) / span) * (chartWidth - pad * 2);
  const y = (move: number) => chartHeight - pad - (Math.min(move, yMax) / yMax) * (chartHeight - pad * 2);
  const thresholdY = y(reactionBps);

  const reset = () => {
    setMinPersistence(2); setScale("all"); setKind("all"); setReactionBps(25);
    setStartAnchor(0); setEndAnchor(167); setInverse(false);
  };

  const copyHypothesis = async () => {
    const text = [
      "Market Structure Sandbox candidate hypothesis",
      `sample: ${formatDate(startAnchor)} → ${formatDate(endAnchor)}`,
      `minimum persistence: ${minPersistence} scales`,
      `required scale: ${scale}`,
      `level kind: ${kind}`,
      `outcome: ${inverse ? "non-reaction / failure" : "reaction"}`,
      `reaction threshold: ${reactionBps} bps`,
      `touch threshold: ${V0_TOUCH_BPS} bps (fixed by stored artifact)`,
      `reaction horizon: ${V0_REACTION_WINDOW_MINUTES}m after touch (fixed by stored artifact)`,
      `forward window: ${V0_FORWARD_HOURS}h (fixed by stored artifact)`,
      "IMPORTANT: exploratory only; freeze before testing on untouched data.",
    ].join("\n");
    await navigator.clipboard?.writeText(text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };

  return (
    <section className="panel">
      <div className="row" style={{ alignItems: "center", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
        <div>
          <div className="panel-sub">SANDBOX · REAL V0 EVENT RECORDS · EXPLORATORY ONLY</div>
          <h2 style={{ margin: "0.2rem 0 0.35rem" }}>Move the dials and watch the historical result change.</h2>
        </div>
        <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap" }}>
          <button type="button" className="btn" onClick={reset}>Reset to V0</button>
          <button type="button" className="btn" onClick={copyHypothesis}>{copied ? "Copied" : "Copy candidate hypothesis"}</button>
        </div>
      </div>
      <p style={{ maxWidth: "980px", marginTop: 0 }}>
        This is the microscope, not the paper. It re-filters the 168 untouched V0 anchors and reclassifies their stored post-touch moves. Nothing you do here changes the locked V0 conclusion. If a pattern looks interesting, copy it as a candidate and test it later on fresh data.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "0.65rem" }}>
        <Control label="Minimum persistence" note="V0 stored only levels with persistence ≥2.">
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
        <Control label="Reaction size" note={`Within the fixed ${V0_REACTION_WINDOW_MINUTES}m post-touch window.`}>
          <input aria-label="Reaction threshold" type="range" min={5} max={100} step={5} value={reactionBps} onChange={(event) => setReactionBps(Number(event.target.value))} />
          <strong>{reactionBps} bps · {(reactionBps / 100).toFixed(2)}%</strong>
        </Control>
        <Control label="Outcome definition" note="Inverse here means non-reaction, not automatically a profitable opposite trade.">
          <select value={inverse ? "inverse" : "reaction"} onChange={(event) => setInverse(event.target.value === "inverse")}>
            <option value="reaction">Reaction / move away</option><option value="inverse">Non-reaction / failure</option>
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

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(175px, 1fr))", gap: "0.55rem", marginTop: "0.8rem" }}>
        <div className="panel compact"><div className="panel-sub">Detected levels</div><strong>{stats.detSuccess} / {stats.detTouched}</strong><div className="panel-sub">{pct(stats.detRate)} {inverse ? "non-reaction" : "reaction"} rate</div></div>
        <div className="panel compact"><div className="panel-sub">Matched controls</div><strong>{stats.baseSuccess} / {stats.baseTouched}</strong><div className="panel-sub">{pct(stats.baseRate)} {inverse ? "non-reaction" : "reaction"} rate</div></div>
        <div className="panel compact"><div className="panel-sub">Difference</div><strong>{signedPp(stats.delta)}</strong><div className="panel-sub">detector minus control</div></div>
        <div className="panel compact"><div className="panel-sub">Filtered candidate pairs</div><strong>{filtered.length}</strong><div className="panel-sub">from 225 frozen detector/control pairs</div></div>
      </div>

      <div className="panel compact" style={{ marginTop: "0.8rem", overflowX: "auto" }}>
        <div className="row" style={{ justifyContent: "space-between", gap: "0.7rem", flexWrap: "wrap" }}>
          <div><div className="panel-sub">TOUCHED DETECTOR EVENTS · MAX MOVE AWAY AFTER TOUCH</div><strong>See where the threshold cuts the observations.</strong></div>
          <div className="panel-sub">circle = detector · faint square = matched control · line = current threshold</div>
        </div>
        {chartRows.length ? <svg role="img" aria-label="Historical touched level outcomes" viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: "100%", minWidth: "680px", marginTop: "0.5rem" }}>
          <line x1={pad} x2={chartWidth - pad} y1={thresholdY} y2={thresholdY} stroke="currentColor" strokeDasharray="6 5" opacity="0.55" />
          <text x={pad + 4} y={Math.max(14, thresholdY - 6)} fill="currentColor" fontSize="11">{reactionBps} bps threshold</text>
          {chartRows.map((row, index) => {
            const detectorSuccess = inverse ? row[7] < reactionBps : row[7] >= reactionBps;
            const baseSuccess = inverse ? row[9] < reactionBps : row[9] >= reactionBps;
            const px = x(row[0]);
            return <g key={`${row[0]}-${row[2]}-${index}`}>
              {row[8] === 1 ? <rect x={px - 3} y={y(row[9]) - 3} width="6" height="6" fill={baseSuccess ? "#22c55e" : "#ef4444"} opacity="0.28" /> : null}
              <circle cx={px} cy={y(row[7])} r="3.4" fill={detectorSuccess ? "#22c55e" : "#ef4444"} opacity="0.9"><title>{`${formatDate(row[0])} · level ${row[2]} · move ${row[7]} bps · persistence ${row[3]}`}</title></circle>
            </g>;
          })}
          <line x1={pad} x2={chartWidth - pad} y1={chartHeight - pad} y2={chartHeight - pad} stroke="currentColor" opacity="0.25" />
          <text x={pad} y={chartHeight - 8} fill="currentColor" fontSize="11">{formatDate(startAnchor)}</text>
          <text x={chartWidth - pad - 86} y={chartHeight - 8} fill="currentColor" fontSize="11">{formatDate(endAnchor)}</text>
        </svg> : <p className="panel-sub">No touched detector events match these filters.</p>}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.6rem", marginTop: "0.8rem" }}>
        <div className="panel compact"><div className="panel-sub">Touch distance</div><strong>{V0_TOUCH_BPS} bps · locked in artifact</strong><div className="panel-sub">To make this a dial we need raw price-path replay, because untouched records do not store minimum distance-to-level.</div></div>
        <div className="panel compact"><div className="panel-sub">Reaction horizon</div><strong>{V0_REACTION_WINDOW_MINUTES} minutes · locked in artifact</strong><div className="panel-sub">Raw replay will let us sweep 15m / 30m / 1h / 4h instead of pretending the stored event record can.</div></div>
        <div className="panel compact"><div className="panel-sub">Forward window</div><strong>{V0_FORWARD_HOURS} hours · locked in artifact</strong><div className="panel-sub">This is the next backend expansion alongside bounce-vs-breakout directionality.</div></div>
      </div>

      <details style={{ marginTop: "0.9rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 700 }}>Show example events under the current filters</summary>
        <div style={{ display: "grid", gap: "0.45rem", marginTop: "0.55rem" }}>
          {filtered.slice(0, 12).map((row, index) => <div key={`${row[0]}-${row[2]}-detail-${index}`} className="panel compact">
            <strong>{formatDate(row[0])} · {row[2].toFixed(3)} CAD</strong>
            <div className="panel-sub">last price {row[1].toFixed(3)} · persistence {row[3]} · {KIND_LABELS[row[5]] ?? "unknown"} · detector {row[6] ? `${row[7].toFixed(1)} bps after touch` : "not touched"} · control {row[8] ? `${row[9].toFixed(1)} bps` : "not touched"}</div>
          </div>)}
        </div>
      </details>
    </section>
  );
}
