type ScaleEvidence = {
  scale: string;
  fit: string;
  fit_reason?: string | null;
  observations?: number | null;
  range_bps?: number | null;
  median_spread_bps?: number | null;
  spread_to_range_ratio?: number | null;
  max_gap_seconds?: number | null;
  zones?: Array<{ center: number; kind: string; touches: number; strength: string }>;
};

type PersistentLevel = {
  center: number;
  scales: string[];
  persistence: number;
  kind: string;
  touches_total: number;
  strength: string;
};

type MultiScalePayload = {
  schema_version?: string;
  generated_at?: string;
  status?: string;
  source?: string;
  currency?: string;
  method?: string;
  scales?: ScaleEvidence[];
  persistent_levels?: PersistentLevel[];
};

function fmt(value: number | null | undefined, digits = 2) {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "—";
}

function isInfraFailure(status: string | undefined) {
  return status === "UNAVAILABLE" || status === "NOT CONFIGURED" || status === "ERROR";
}

function fitMeaning(fit: string): string {
  if (fit === "USABLE") return "Enough movement relative to noise to study structure here.";
  if (fit === "MARGINAL") return "Some structure may be visible, but noise is still a large part of the move.";
  if (fit === "POOR") return "Too noisy for this horizon; spread/noise overwhelms the move.";
  if (fit === "INSUFFICIENT") return "Not enough usable history yet for this horizon.";
  return "Fit has not been classified.";
}

export function MultiScaleStructureProbe({
  payload,
  sourceStatus,
  sourceDetail,
}: {
  payload: unknown;
  sourceStatus?: string;
  sourceDetail?: string;
}) {
  const data = (payload ?? null) as MultiScalePayload | null;
  if (!data || !Array.isArray(data.scales)) {
    const unavailable = isInfraFailure(sourceStatus);
    return (
      <section className="panel compact">
        <div className="panel-sub">LIVE MARKET STATE · DETECTOR</div>
        <div className="row" style={{ alignItems: "center", gap: "0.75rem" }}>
          <h2 style={{ margin: 0 }}>{unavailable ? "Market structure engine unavailable" : "Waiting for live structure"}</h2>
          <span className="tag muted">{sourceStatus ?? "WAITING"}</span>
        </div>
        <p className="panel-sub" style={{ marginBottom: 0, marginTop: "0.75rem" }}>
          {sourceDetail ?? "This section shows what the detector sees right now. It is separate from whether those patterns have been validated as useful."}
        </p>
      </section>
    );
  }

  const levels = Array.isArray(data.persistent_levels) ? data.persistent_levels : [];
  const schemaLabel = data.schema_version ?? "market-structure.v1";

  return (
    <section className="panel compact">
      <div className="panel-sub">LIVE MARKET STATE · {schemaLabel}</div>
      <div className="row" style={{ alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
        <h2 style={{ margin: 0 }}>What the detector sees right now</h2>
        <span className="tag muted">{data.status ?? sourceStatus ?? "OK"}</span>
      </div>
      <p style={{ marginBottom: "0.35rem" }}>
        The detector checks the same structure logic at several horizons. A horizon can be usable even when a shorter one is too noisy.
      </p>
      <p className="panel-sub" style={{ marginTop: 0 }}>
        <strong>Important:</strong> detected structure is not the same thing as validated predictive value. This section answers “what do we see?”, not “does it work?”
        {data.source ? ` Source: ${data.source}.` : ""}
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(175px, 1fr))", gap: "0.5rem" }}>
        {data.scales.map((scale) => (
          <div key={scale.scale} className="panel compact">
            <div className="panel-sub">{scale.scale} HORIZON</div>
            <strong>{scale.fit}</strong>
            <p className="panel-sub" style={{ margin: "0.35rem 0 0" }}>{fitMeaning(scale.fit)}</p>
            <div className="panel-sub" style={{ marginTop: "0.4rem" }}>{scale.zones?.length ?? 0} candidate zones</div>
            <details style={{ marginTop: "0.55rem" }}>
              <summary style={{ cursor: "pointer" }}>Why?</summary>
              <div className="panel-sub" style={{ marginTop: "0.4rem" }}>
                {scale.fit_reason ? <><strong>{scale.fit_reason}</strong><br /></> : null}
                range {fmt(scale.range_bps)} bps<br />
                spread/range {fmt(scale.spread_to_range_ratio, 2)}×<br />
                max gap {fmt(scale.max_gap_seconds, 1)}s<br />
                observations {scale.observations ?? "—"}
              </div>
            </details>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "1rem" }}>
        <div className="panel-sub">CANDIDATE LEVELS SEEN ON MULTIPLE HORIZONS</div>
        <p className="panel-sub" style={{ margin: "0.25rem 0 0.5rem" }}>
          These are recurring price areas the detector sees across scales. They are research candidates, not proven support/resistance and not trade signals.
        </p>
        {levels.length > 0 ? (
          <div style={{ display: "grid", gap: "0.5rem", marginTop: "0.5rem" }}>
            {levels.map((level, index) => (
              <div key={`${level.center}-${index}`} className="panel compact">
                <strong>{fmt(level.center, 3)} {data.currency ?? ""}</strong>
                <div className="panel-sub">
                  Seen on {level.scales.join(" + ")} · {level.touches_total} detector pivot touches · {level.kind} candidate
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="panel-sub" style={{ marginBottom: 0, marginTop: "0.5rem" }}>
            No candidate level currently persists across enough horizons.
          </p>
        )}
      </div>

      <details style={{ marginTop: "0.8rem" }}>
        <summary style={{ cursor: "pointer" }}>Engine details</summary>
        <p className="panel-sub" style={{ marginBottom: 0 }}>
          {sourceDetail ?? "Structure is loaded from the market-structure engine."}
          {data.generated_at ? ` Generated ${data.generated_at}.` : ""}
          {data.method ? ` Method: ${data.method}.` : ""}
        </p>
      </details>
    </section>
  );
}
