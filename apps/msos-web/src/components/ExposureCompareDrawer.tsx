"use client";

import {
  fitLensLabel,
  formatLegsOneLine,
  leverageChipLabel,
  liquidityChipLabel,
  timeBoundChipLabel,
  type ExposurePathRecord,
  type FitLensId,
} from "@/lib/ppeExposureMenu";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";

type ExposureCompareDrawerProps = {
  paths: [ExposurePathRecord, ExposurePathRecord];
  footerCopy: string;
  open: boolean;
  onClose: () => void;
};

function compareCell(path: ExposurePathRecord, formatMoney: (value: number) => string): string {
  if (typeof path.cost_hint_usd === "number" && Number.isFinite(path.cost_hint_usd)) {
    return formatMoney(path.cost_hint_usd);
  }
  return "—";
}

export function ExposureCompareDrawer({
  paths,
  footerCopy,
  open,
  onClose,
}: ExposureCompareDrawerProps) {
  const { formatMoney } = useDisplayCurrency();
  if (!open) {
    return null;
  }

  const [left, right] = paths;

  const rows: { label: string; left: string; right: string }[] = [
    { label: "Illustrative cost", left: compareCell(left, formatMoney), right: compareCell(right, formatMoney) },
    { label: "Capital at risk", left: left.capital_shape, right: right.capital_shape },
    {
      label: "Leverage",
      left: leverageChipLabel(left.leverage),
      right: leverageChipLabel(right.leverage),
    },
    {
      label: "Time",
      left: timeBoundChipLabel(left.time_bound),
      right: timeBoundChipLabel(right.time_bound),
    },
    {
      label: "Liquidity",
      left: liquidityChipLabel(left.liquidity),
      right: liquidityChipLabel(right.liquidity),
    },
    { label: "Trust", left: left.trust_badge, right: right.trust_badge },
    { label: "Structure", left: formatLegsOneLine(left.legs), right: formatLegsOneLine(right.legs) },
    {
      label: "Fits",
      left: (left.fit_lenses ?? []).map((id) => fitLensLabel(id as FitLensId)).join(" · ") || "—",
      right: (right.fit_lenses ?? []).map((id) => fitLensLabel(id as FitLensId)).join(" · ") || "—",
    },
  ];

  return (
    <div className="exposure-compare-backdrop" role="presentation" onClick={onClose}>
      <aside
        className="exposure-compare-drawer panel"
        role="dialog"
        aria-labelledby="exposure-compare-title"
        aria-modal="true"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="exposure-compare-head">
          <div>
            <p className="eyebrow">Compare paths</p>
            <h2 id="exposure-compare-title">Side-by-side illustration</h2>
          </div>
          <button type="button" className="btn slim ghost" onClick={onClose}>
            Close
          </button>
        </header>

        <div className="exposure-compare-columns">
          <div>
            <h3>{left.label}</h3>
          </div>
          <div>
            <h3>{right.label}</h3>
          </div>
        </div>

        <dl className="exposure-compare-grid">
          {rows.map((row) => (
            <div key={row.label} className="exposure-compare-row">
              <dt>{row.label}</dt>
              <dd>{row.left}</dd>
              <dd>{row.right}</dd>
            </div>
          ))}
        </dl>

        <footer className="exposure-compare-footer panel-sub">
          <p>{footerCopy}</p>
        </footer>
      </aside>
    </div>
  );
}
