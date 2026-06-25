"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { restorePaperTrade } from "@/lib/expressionPersistence";
import { clearPaperTradeUndo, peekPaperTradeUndo } from "@/lib/paperTradeUndo";

export function MonitorDeleteNotice() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const deleted = searchParams.get("deleted") === "1";
  const titleParam = searchParams.get("title");
  const [canUndo, setCanUndo] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCanUndo(Boolean(peekPaperTradeUndo()));
  }, [deleted, titleParam]);

  if (!deleted) {
    return null;
  }

  const snapshot = peekPaperTradeUndo();
  const title = titleParam?.trim() || snapshot?.expression.planHeadline || "Paper trade";

  function clearNotice() {
    clearPaperTradeUndo();
    router.replace("/monitor");
  }

  async function handleUndo() {
    const undo = peekPaperTradeUndo();
    if (!undo) {
      setError("Undo expired — trade data is no longer available.");
      return;
    }
    setBusy(true);
    setError(null);
    const ok = await restorePaperTrade(undo.expression);
    if (ok) {
      clearPaperTradeUndo();
      router.replace("/monitor");
      router.refresh();
      return;
    }
    setError("Could not restore paper trade — try again.");
    setBusy(false);
  }

  return (
    <div className="monitor-delete-notice" role="status" aria-live="polite">
      <p>
        <strong>{title}</strong> was deleted successfully.
      </p>
      <div className="monitor-delete-notice-actions">
        {canUndo && snapshot ? (
          <button type="button" className="btn slim primary" disabled={busy} onClick={() => void handleUndo()}>
            {busy ? "Restoring…" : "Undo"}
          </button>
        ) : null}
        <button type="button" className="btn slim" disabled={busy} onClick={clearNotice}>
          Dismiss
        </button>
      </div>
      {error ? <p className="micro monitor-delete-notice-error">{error}</p> : null}
    </div>
  );
}
