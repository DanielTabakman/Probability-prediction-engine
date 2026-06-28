import Link from "next/link";

import { PaperTradeRowActions } from "@/components/PaperTradeManageActions";
import { effectivePaperTradeStatus } from "@/lib/msosWorkflowStore";
import type { StoredExpression } from "@/lib/msosWorkflowStore";
import {
  displayCurrencyDisclaimer,
  formatMoney,
  type DisplayCurrency,
} from "@/lib/displayCurrency";
import { resolveDisplayAssetMeta } from "@/lib/ppeDisplayPayload";
import { DEMO_FOOTER } from "@/lib/publicCopy";

type Props = {
  trade: StoredExpression;
  currentSpotUsd: number | null;
  displayCurrency?: DisplayCurrency;
};

function statusLabel(status: string): string {
  if (status === "closed") return "Closed";
  if (status === "expired") return "Expired";
  return "Open";
}

export function PaperTradeDetailContent({
  trade,
  currentSpotUsd,
  displayCurrency = "USD",
}: Props) {
  const fmt = (usd: number) => formatMoney(usd, displayCurrency);
  const status = effectivePaperTradeStatus(trade);
  const mark = trade.markAtSave;
  const belief = trade.beliefSnapshot;
  const instrumentLabel =
    trade.instrument?.trim() ||
    resolveDisplayAssetMeta(null).instrument_label ||
    "Options";

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Monitor · Paper trade</div>
          <h1 className="title">{trade.planHeadline}</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot teal" aria-hidden="true" />
            {statusLabel(status)}
          </span>
          <Link href="/monitor" className="btn slim">
            Back to monitor
          </Link>
        </div>
      </header>

      <section className="panel paper-trade-detail">
        <p className="micro display-currency-note">{displayCurrencyDisclaimer(displayCurrency)}</p>
        <div className="panel-head">
          <div>
            <h2>Plan summary</h2>
            <div className="panel-sub">{trade.planSummary}</div>
          </div>
          <span className="tag teal">Paper</span>
        </div>

        <div className="semantic-lock">
          <div className="lock">
            <h3>Instrument</h3>
            <p>{instrumentLabel}</p>
          </div>
          <div className="lock">
            <h3>Expiry</h3>
            <p>{trade.expiryDate ?? "—"}</p>
          </div>
          <div className="lock">
            <h3>Saved</h3>
            <p>{trade.savedAt ?? trade.updatedAt}</p>
          </div>
        </div>

        {belief ? (
          <div className="panel compact">
            <h3>Belief at save</h3>
            <p>
              Forward ×{belief.forwardMult.toFixed(2)} · vol ×{belief.volMult.toFixed(2)}
            </p>
          </div>
        ) : null}

        {mark ? (
          <div className="panel compact">
            <h3>Marks at save</h3>
            <div className="line">
              <span>Spot</span>
              <strong>{typeof mark.spotUsd === "number" ? fmt(mark.spotUsd) : "—"}</strong>
            </div>
            {currentSpotUsd != null ? (
              <div className="line">
                <span>Spot now</span>
                <strong>{fmt(currentSpotUsd)}</strong>
              </div>
            ) : null}
            <div className="line">
              <span>Max loss</span>
              <strong>
                {typeof mark.maxLossUsd === "number" ? fmt(Math.abs(mark.maxLossUsd)) : "—"}
              </strong>
            </div>
            <div className="line">
              <span>Max gain</span>
              <strong>
                {typeof mark.maxGainUsd === "number" ? fmt(mark.maxGainUsd) : "—"}
              </strong>
            </div>
          </div>
        ) : null}

        <div className="panel compact">
          <h3>Legs ({trade.legs.length})</h3>
          {trade.legs.map((leg, index) => (
            <div key={`${leg.side}-${leg.instrument}-${index}`} className="line">
              <span>
                {leg.side} {leg.instrument} · {leg.strike}
              </span>
              <strong>{leg.tenor}</strong>
            </div>
          ))}
        </div>

        <PaperTradeRowActions trade={trade} status={status} />
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
