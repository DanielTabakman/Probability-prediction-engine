import type {
  MarketMovedSinceObservation,
  MarketMovedSinceSummary,
} from "@/lib/marketMovedSince";

type MarketMovedSinceCardProps = {
  value: MarketMovedSinceSummary;
};

function ObservationBlock({
  title,
  observation,
}: {
  title: string;
  observation: MarketMovedSinceObservation;
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

export function MarketMovedSinceCard({ value }: MarketMovedSinceCardProps) {
  const changeTone =
    value.input_status === "comparable"
      ? "teal"
      : value.input_status === "missing" || value.input_status === "incomparable"
        ? ""
        : "amber";
  return (
    <div data-testid="market-moved-since-card">
      <div className="panel-head">
        <div>
          <h2>Since you last looked</h2>
          <div className="panel-sub">
            Last-seen versus now for this saved Region Bet. Paper observation only.
          </div>
        </div>
        <span className="tag teal">Paper</span>
      </div>

      <div className="score" aria-label="Last-seen versus now observation times">
        <div className="small-panel">
          <div className="k">Last seen</div>
          <div className="v">{value.last_seen_at_label}</div>
        </div>
        <div className="small-panel">
          <div className="k">Now</div>
          <div className="v">{value.now_at_label}</div>
        </div>
        <div className="small-panel">
          <div className="k">Change</div>
          <div className={changeTone ? `v ${changeTone}` : "v"}>{value.change.delta_display}</div>
          <p className="micro">{value.change.direction_label}</p>
        </div>
        <div className="small-panel">
          <div className="k">Inputs</div>
          <div className={changeTone ? `v ${changeTone}` : "v"}>{value.input_status_label}</div>
        </div>
      </div>

      <div className="score" aria-label="Last-seen versus now underlying">
        <ObservationBlock title="Last-seen underlying" observation={value.last_seen} />
        <ObservationBlock title="Now underlying" observation={value.now} />
      </div>

      <div aria-label="Observable change notes">
        {value.notes.map((note) => (
          <p className="micro" key={note}>
            {note}
          </p>
        ))}
      </div>
      <p className="micro">{value.limitation}</p>
    </div>
  );
}
