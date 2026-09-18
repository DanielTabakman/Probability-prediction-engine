import type { RegionBetLabeledObservation, RegionBetMonitorValue } from "@/lib/regionBetMonitor";

type RegionBetMonitorCardProps = {
  value: RegionBetMonitorValue;
};

function ObservationBlock({
  title,
  observation,
}: {
  title: string;
  observation: RegionBetLabeledObservation;
}) {
  const tone =
    observation.quality === "observed"
      ? "teal"
      : observation.quality === "unavailable"
        ? ""
        : "amber";
  return (
    <div className="small-panel">
      <div className="k">{title}</div>
      <div className={tone ? `v ${tone}` : "v"}>{observation.display}</div>
      <p className="micro">
        {observation.quality_label} · {observation.observed_at_label}
      </p>
    </div>
  );
}

export function RegionBetMonitorCard({ value }: RegionBetMonitorCardProps) {
  return (
    <div data-testid="region-bet-monitor-card">
      <div className="panel-head">
        <div>
          <h2>Region Bet then / now</h2>
          <div className="panel-sub">
            Underlying observations are separate from paper-expression values. Paper only.
          </div>
        </div>
        <span className="tag teal">Paper</span>
      </div>

      <div className="panel-head compact">
        <h3>Underlying</h3>
        <span className="tag">{value.underlying.vs_region_label}</span>
      </div>
      <div className="score" aria-label="Underlying then versus now">
        <ObservationBlock title="Entry underlying" observation={value.underlying.entry} />
        <ObservationBlock title="Current underlying" observation={value.underlying.current} />
      </div>

      <div className="panel-head compact">
        <h3>Paper expression</h3>
        <span className="tag amber">{value.expression_id ?? "No expression id"}</span>
      </div>
      <div className="score" aria-label="Paper-expression then versus now">
        <ObservationBlock title="Entry paper-expression" observation={value.expression.entry} />
        <ObservationBlock title="Current paper-expression" observation={value.expression.current} />
      </div>

      <div aria-label="Value drivers">
        {value.value_drivers.map((driver) => (
          <p className="micro" key={driver}>
            {driver}
          </p>
        ))}
      </div>
      <p className="micro">{value.limitation}</p>
    </div>
  );
}
