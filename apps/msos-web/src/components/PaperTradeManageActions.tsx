"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { PaperTradeSummary } from "@/lib/monitorHistoryFeed";
import {
  clearAllPaperTrades,
  closePaperTradeById,
  deletePaperTradeById,
} from "@/lib/expressionPersistence";

type Props = {
  trades: PaperTradeSummary[];
  variant?: "monitor" | "history";
};

export function PaperTradeManageActions({ trades, variant = "monitor" }: Props) {
  const router = useRouter();
  const [busyId, setBusyId] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  if (trades.length === 0) {
    return null;
  }

  async function refreshAfter(action: () => Promise<boolean>, okMessage: string, failMessage: string) {
    const ok = await action();
    setMessage(ok ? okMessage : failMessage);
    if (ok) {
      router.refresh();
    }
  }

  async function handleClearAll() {
    if (!window.confirm(`Remove all ${trades.length} paper trades from your workspace?`)) {
      return;
    }
    setClearing(true);
    await refreshAfter(clearAllPaperTrades, "All paper trades cleared.", "Could not clear paper trades.");
    setClearing(false);
  }

  async function handleDelete(tradeId: string, title: string) {
    if (!window.confirm(`Delete paper trade “${title}”?`)) {
      return;
    }
    setBusyId(tradeId);
    await refreshAfter(
      () => deletePaperTradeById(tradeId),
      "Paper trade deleted.",
      "Could not delete paper trade.",
    );
    setBusyId(null);
  }

  async function handleClose(tradeId: string) {
    setBusyId(tradeId);
    await refreshAfter(
      () => closePaperTradeById(tradeId),
      "Paper trade marked closed.",
      "Could not close paper trade.",
    );
    setBusyId(null);
  }

  return (
    <div className={`paper-trade-manage paper-trade-manage-${variant}`}>
      <div className="panel-head compact">
        <h2>Manage paper trades</h2>
        <div className="panel-sub">Remove mistakes or mark positions closed — no live orders.</div>
      </div>
      {variant === "history" ? (
        <ul className="paper-trade-manage-list">
          {trades.map((trade) => (
            <li key={trade.id} className="paper-trade-manage-row">
              <span>
                {trade.title} · {trade.status}
              </span>
              <span className="paper-trade-manage-buttons">
                {trade.status === "open" ? (
                  <button
                    type="button"
                    className="btn slim"
                    disabled={busyId === trade.id}
                    onClick={() => void handleClose(trade.id)}
                  >
                    Close
                  </button>
                ) : null}
                <button
                  type="button"
                  className="btn slim dark"
                  disabled={busyId === trade.id}
                  onClick={() => void handleDelete(trade.id, trade.title)}
                >
                  Delete
                </button>
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="paper-trade-manage-toolbar">
          <button
            type="button"
            className="btn slim dark"
            disabled={clearing}
            onClick={() => void handleClearAll()}
          >
            {clearing ? "Clearing…" : "Clear all paper trades"}
          </button>
        </div>
      )}
      {message ? (
        <p className="micro persistence-note" role="status">
          {message}
        </p>
      ) : null}
    </div>
  );
}

export function PaperTradeRowActions({
  tradeId,
  title,
  status,
}: {
  tradeId: string;
  title: string;
  status: string;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function run(action: () => Promise<boolean>, okMessage: string) {
    setBusy(true);
    const ok = await action();
    setMessage(ok ? okMessage : "Action failed — try again.");
    if (ok) router.refresh();
    setBusy(false);
  }

  return (
    <div className="paper-trade-detail-actions">
      {status === "open" ? (
        <button
          type="button"
          className="btn slim"
          disabled={busy}
          onClick={() => void run(() => closePaperTradeById(tradeId), "Marked closed.")}
        >
          Mark closed
        </button>
      ) : null}
      <button
        type="button"
        className="btn slim dark"
        disabled={busy}
        onClick={() => {
          if (window.confirm(`Delete paper trade “${title}”?`)) {
            void run(() => deletePaperTradeById(tradeId), "Deleted.");
          }
        }}
      >
        Delete
      </button>
      {message ? (
        <p className="micro" role="status">
          {message}
        </p>
      ) : null}
    </div>
  );
}
