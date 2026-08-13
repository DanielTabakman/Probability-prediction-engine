type ScaleEvidence = {
  scale: string;
  fit: string;
  fit_reason?: string;
  observations?: number;
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

export function MultiScaleStructureProbe({ payload }: { payload: unknown }) {
  const data = (payload ?? null) as MultiScalePayload | null;
  if (!data || !Array.isArray(data.scales)) {
    return (
      <section className="panel compact">
        <div className="panel-sub">MULTI-SCALE STRUCTURE</div>
        <h2 style={{ marginBottom: "0.35rem" }}>Waiting for structure evidence</h2>
        <p className="panel-sub" style={{ marginBottom: 0 }}>
          The same detector will be applied at 5m, 15m, 1h, 4h, and 1d without choosing one privileged zoom level.
        </p>
      </section>
    );
  }

  const levels = Array.isArray(data.persistent_levels) ? data.persistent_levels : [];

  return (
    <section className="panel compact">
      <div className="panel-sub">MULTI-SCALE STRUCTURE · EXPERIMENTAL</div>
      <h2 style={{ marginBottom: "0.35rem" }}>Where does structure survive when we zoom?</h2>
      <p className="panel-sub">
        One relative pivot/zone detector is reused at every horizon. Feed fitness is judged separately at each scale; this is evidence, not a trade signal.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.5rem" }}>
        {data.scales.map((scale) => (
          <div key={scale.scale} className="panel compact">
            <div className="panel-sub">{scale.scale}</div>
            <strong>{scale.fit}</strong>
            <div className="panel-sub" style={{ marginTop: "0.4rem" }}>
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
