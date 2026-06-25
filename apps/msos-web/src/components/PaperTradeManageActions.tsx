"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { PaperTradeSummary } from "@/lib/monitorHistoryFeed";
import type { PaperTradeStatus } from "@/lib/expressionPersistence";
import type { StoredExpression } from "@/lib/msosWorkflowStore";
import {
  clearAllPaperTrades,
  closePaperTradeById,
  deletePaperTradeById,
} from "@/lib/expressionPersistence";
import { clearPaperTradeUndo, stashPaperTradeUndo } from "@/lib/paperTradeUndo";
import { goToMonitorAfterDelete } from "@/lib/monitorNav";

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
  trade,
  status,
}: {
  trade: StoredExpression;
  status: PaperTradeStatus;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const title = trade.planHeadline;

  async function runClose() {
    setBusy(true);
    const ok = await closePaperTradeById(trade.id);
    setMessage(ok ? "Marked closed." : "Action failed — try again.");
    if (ok) router.refresh();
    setBusy(false);
  }

  async function runDelete() {
    if (!window.confirm(`Delete paper trade “${title}”?`)) {
      return;
    }
    setBusy(true);
    stashPaperTradeUndo(trade);
    const ok = await deletePaperTradeById(trade.id);
    if (ok) {
      goToMonitorAfterDelete(title);
      return;
    }
    clearPaperTradeUndo();
    setMessage("Could not delete paper trade — try again.");
    setBusy(false);
  }

  return (
    <div className="paper-trade-detail-actions">
      {status === "open" ? (
        <button type="button" className="btn slim" disabled={busy} onClick={() => void runClose()}>
          Mark closed
        </button>
      ) : null}
      <button type="button" className="btn slim dark" disabled={busy} onClick={() => void runDelete()}>
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
