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
        <div className="panel-sub">MULTI-SCALE STRUCTURE · ENGINE</div>
        <div className="row" style={{ alignItems: "center", gap: "0.75rem" }}>
          <h2 style={{ margin: 0 }}>{unavailable ? "Market structure engine unavailable" : "Waiting for structure evidence"}</h2>
          <span className="tag muted">{sourceStatus ?? "WAITING"}</span>
        </div>
        <p className="panel-sub" style={{ marginBottom: 0, marginTop: "0.75rem" }}>
          {sourceDetail ??
            "Capture health stays independent. Structure is loaded from market-structure.v1 when the engine is reachable."}
        </p>
      </section>
    );
  }

  const levels = Array.isArray(data.persistent_levels) ? data.persistent_levels : [];
  const schemaLabel = data.schema_version ?? "market-structure.v1";

  return (
    <section className="panel compact">
      <div className="panel-sub">MULTI-SCALE STRUCTURE · {schemaLabel}</div>
      <div className="row" style={{ alignItems: "center", gap: "0.75rem" }}>
        <h2 style={{ margin: 0 }}>Where does structure survive when we zoom?</h2>
        <span className="tag muted">{data.status ?? sourceStatus ?? "OK"}</span>
      </div>
      <p className="panel-sub">
        Evidence comes from the market-structure engine. Feed fitness is judged separately at each scale; this is not a trade signal.
        {data.source ? ` Source ${data.source}.` : ""}
        {data.generated_at ? ` Generated ${data.generated_at}.` : ""}
      </p>
      {sourceDetail ? <p className="panel-sub">{sourceDetail}</p> : null}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.5rem" }}>
        {data.scales.map((scale) => (
          <div key={scale.scale} className="panel compact">
            <div className="panel-sub">{scale.scale}</div>
            <strong>{scale.fit}</strong>
            <div className="panel-sub" style={{ marginTop: "0.4rem" }}>
              {scale.fit_reason ? (
                <>
                  {scale.fit_reason}
                  <br />
                </>
              ) : null}
              range {fmt(scale.range_bps)} bps
              <br />
              spread/range {fmt(scale.spread_to_range_ratio, 2)}×
              <br />
              max gap {fmt(scale.max_gap_seconds, 1)}s
              <br />
              zones {scale.zones?.length ?? 0}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "1rem" }}>
        <div className="panel-sub">PERSISTENT LEVELS</div>
        {levels.length > 0 ? (
          <div style={{ display: "grid", gap: "0.5rem", marginTop: "0.5rem" }}>
            {levels.map((level, index) => (
              <div key={`${level.center}-${index}`} className="panel compact">
                <strong>{fmt(level.center, 3)} {data.currency ?? ""}</strong>
                <div className="panel-sub">
                  {level.kind} · {level.strength} · {level.scales.join(" + ")} · {level.touches_total} pivot touches
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="panel-sub" style={{ marginBottom: 0, marginTop: "0.5rem" }}>
            No level has persisted across enough currently available horizons yet.
          </p>
        )}
      </div>
    </section>
  );
}
