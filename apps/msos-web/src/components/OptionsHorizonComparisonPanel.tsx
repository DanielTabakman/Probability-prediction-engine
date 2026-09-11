import type { OptionsHorizonComparisonPayload } from "@/lib/optionsHorizonComparison";

type OptionsHorizonComparisonPanelProps = {
  comparison: OptionsHorizonComparisonPayload;
};

function formatUsd(value: number | null, digits = 0): string {
  if (value === null || !Number.isFinite(value)) return "Unavailable";
  return `$${value.toLocaleString("en-US", { maximumFractionDigits: digits })}`;
}

function formatPercent(value: number | null): string {
  if (value === null || !Number.isFinite(value)) return "Unavailable";
  return `${(value * 100).toFixed(1)}%`;
}

function formatFlags(flags: string[]): string {
  return flags.length ? flags.map((flag) => flag.replace(/_/g, " ")).join(", ") : "OK";
}

export function OptionsHorizonComparisonPanel({ comparison }: OptionsHorizonComparisonPanelProps) {
  return (
    <section className="options-horizon-panel" aria-label="Listed option horizon comparison">
      <div>
        <p className="eyebrow">Horizon comparison</p>
        <h2>Listed time windows</h2>
        <p className="micro">
          Compare expiry windows before choosing any expression. Rows are display-only.
        </p>
      </div>

      {comparison.rows.length ? (
        <div className="options-horizon-comparison-table-wrap">
          <table className="options-horizon-comparison-table">
            <thead>
              <tr>
                <th scope="col">Target</th>
                <th scope="col">Expiry</th>
                <th scope="col">Days</th>
                <th scope="col">Forward</th>
                <th scope="col">ATM IV</th>
                <th scope="col">1 sigma</th>
                <th scope="col">Flags</th>
                <th scope="col">Time decay</th>
              </tr>
            </thead>
            <tbody>
              {comparison.rows.map((row) => (
                <tr key={row.expiry_ts}>
                  <td>{row.target_bucket_label}</td>
                  <td>{row.expiry_date}</td>
                  <td>{row.days_out}</td>
                  <td>{formatUsd(row.forward_usd)}</td>
                  <td>{formatPercent(row.atm_iv_annual)}</td>
                  <td>{formatUsd(row.one_sigma_move_usd)}</td>
                  <td>{formatFlags([...row.data_flags, ...row.trust_flags])}</td>
                  <td>{row.time_decay_language}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="micro">No listed future expiries are available for comparison.</p>
      )}

      <p className="micro">{comparison.limitations.join(" ")}</p>
    </section>
  );
}
