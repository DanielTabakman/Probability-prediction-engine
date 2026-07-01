"use client";

import Link from "next/link";
import { useState } from "react";

import {
  buildExpressionPlannerHandoffHref,
  buildStrategyLabHandoffHref,
  fitLensLabel,
  formatLegsOneLine,
  leverageChipLabel,
  liquidityChipLabel,
  railDisplayLabel,
  timeBoundChipLabel,
  trustBadgeTone,
  type ExposurePathRecord,
  type FitLensId,
} from "@/lib/ppeExposureMenu";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";

type ExposurePathCardProps = {
  assetId: string;
  path: ExposurePathRecord;
  activeFitLens: FitLensId | null;
  dimmed: boolean;
  pinned: boolean;
  pinDisabled: boolean;
  onPinToggle: () => void;
};

export function ExposurePathCard({
  assetId,
  path,
  activeFitLens,
  dimmed,
  pinned,
  pinDisabled,
  onPinToggle,
}: ExposurePathCardProps) {
  const { formatMoney } = useDisplayCurrency();
  const [detailsOpen, setDetailsOpen] = useState(false);
  const trustTone = trustBadgeTone(path.trust_badge);
  const showCost = typeof path.cost_hint_usd === "number" && Number.isFinite(path.cost_hint_usd);
  const legsLine = formatLegsOneLine(path.legs);
  const showLegs = legsLine !== "—";

  return (
    <article
      className={`exposure-path-card panel${dimmed ? " exposure-path-card-dimmed" : ""}${pinned ? " exposure-path-card-pinned" : ""}`}
      aria-labelledby={`exposure-path-${path.path_id}`}
    >
      <header className="exposure-path-card-head">
        <div>
          <h2 id={`exposure-path-${path.path_id}`}>{path.label}</h2>
          <p className="panel-sub">{path.headline}</p>
        </div>
        <div className="exposure-path-badges">
          <span className="tag muted">{railDisplayLabel(path.instrument_rail)}</span>
          <span className={`tag ${trustTone}`.trim()}>{path.trust_badge}</span>
        </div>
      </header>

      {showCost ? (
        <p className="exposure-path-cost">
          Illustrative cost: <strong>{formatMoney(path.cost_hint_usd!)}</strong>
        </p>
      ) : null}

      <div className="exposure-path-meta-chips">
        <span className="tag muted">{leverageChipLabel(path.leverage)}</span>
        <span className="tag muted">{timeBoundChipLabel(path.time_bound)}</span>
        <span className="tag muted">{liquidityChipLabel(path.liquidity)}</span>
      </div>

      {path.fit_lenses?.length ? (
        <div className="exposure-path-fit-pills">
          {path.fit_lenses.map((lensId) => (
            <span
              key={lensId}
              className={`tag${activeFitLens === lensId ? " teal" : " muted"}`}
            >
              Fits: {fitLensLabel(lensId)}
            </span>
          ))}
        </div>
      ) : null}

      {showLegs ? <p className="exposure-path-legs panel-sub">Structure: {legsLine}</p> : null}

      <div className="exposure-path-actions">
        <button
          type="button"
          className={`btn slim${pinned ? " active" : ""}`}
          aria-pressed={pinned}
          disabled={pinDisabled}
          onClick={onPinToggle}
        >
          {pinned ? "Pinned" : "Pin to compare"}
        </button>
        <button
          type="button"
          className="btn slim ghost"
          aria-expanded={detailsOpen}
          onClick={() => setDetailsOpen((open) => !open)}
        >
          {detailsOpen ? "Hide details" : "Details"}
        </button>
      </div>

      {detailsOpen ? (
        <div className="exposure-path-details">
          <p className="exposure-path-capital">{path.capital_shape}</p>
          <div className="exposure-path-lists">
            <div>
              <span className="micro">Pros</span>
              <ul>
                {path.pros.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <span className="micro">Cons</span>
              <ul>
                {path.cons.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ) : null}

      {path.instrument_rail === "listed_options" && path.trust_badge !== "Planned" ? (
        <p className="exposure-path-handoff panel-sub">
          Next:{" "}
          <Link href={path.deep_link ?? buildStrategyLabHandoffHref(assetId)}>
            inspect in Strategy Lab
          </Link>
          {" · "}
          <Link href={buildExpressionPlannerHandoffHref(assetId)}>structure fit</Link>
        </p>
      ) : path.deep_link ? (
        <Link href={path.deep_link} className="btn slim">
          Open in Strategy Lab
        </Link>
      ) : null}
    </article>
  );
}
