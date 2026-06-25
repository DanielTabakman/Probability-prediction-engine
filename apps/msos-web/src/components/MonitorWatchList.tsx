"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { MouseEvent } from "react";
import { useState } from "react";

import { deletePaperTradeWithUndo } from "@/lib/expressionPersistence";
import type { MonitorWatchPanel } from "@/lib/monitorHistoryFeed";

type Props = {
  panels: MonitorWatchPanel[];
};

export function MonitorWatchList({ panels }: Props) {
  const router = useRouter();
  const [busyId, setBusyId] = useState<string | null>(null);

  async function handleDelete(event: MouseEvent, tradeId: string, title: string) {
    event.preventDefault();
    event.stopPropagation();
    if (!window.confirm(`Delete paper trade “${title}”?`)) {
      return;
    }
    setBusyId(tradeId);
    const result = await deletePaperTradeWithUndo(tradeId);
    if (result.ok) {
      const label = encodeURIComponent(result.title ?? title);
      router.push(`/monitor?deleted=1&title=${label}`);
      router.refresh();
    }
    setBusyId(null);
  }

  return (
    <div className="monitor-watch-list" aria-label="Watch list">
      {panels.map((panel) => {
        const content = (
          <>
            {panel.badge ? (
              <div className="monitor-watch-meta">
                <span className={`tag ${panel.tone}`}>{panel.badge}</span>
              </div>
            ) : null}
            <h3>{panel.title}</h3>
            <p>{panel.body}</p>
            {panel.markLine ? <p className="micro watch-mark">{panel.markLine}</p> : null}
          </>
        );

        if (panel.tradeId) {
          return (
            <div key={panel.id} className="monitor-watch-row monitor-watch-row-with-actions">
              <Link href={panel.href ?? "#"} className="monitor-watch-row-main monitor-watch-link">
                {content}
              </Link>
              <div className="monitor-watch-row-actions">
                <button
                  type="button"
                  className="btn slim dark"
                  disabled={busyId === panel.tradeId}
                  aria-label={`Delete ${panel.title}`}
                  onClick={(event) => void handleDelete(event, panel.tradeId!, panel.title)}
                >
                  {busyId === panel.tradeId ? "…" : "Delete"}
                </button>
              </div>
            </div>
          );
        }

        if (panel.href) {
          return (
            <Link key={panel.id} href={panel.href} className="monitor-watch-row monitor-watch-link">
              {content}
            </Link>
          );
        }

        return (
          <div key={panel.id} className="monitor-watch-row">
            {content}
          </div>
        );
      })}
    </div>
  );
}
