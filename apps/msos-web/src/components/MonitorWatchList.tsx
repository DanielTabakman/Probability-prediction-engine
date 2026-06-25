"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { MouseEvent } from "react";
import { useState } from "react";

import { deletePaperTradeWithUndo } from "@/lib/expressionPersistence";
import { formatMarkLine } from "@/lib/monitorMarkLine";
import type { MonitorWatchPanel } from "@/lib/monitorHistoryFeed";
import { goToMonitorAfterDeleteFromRouter } from "@/lib/monitorNav";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";

type Props = {
  panels: MonitorWatchPanel[];
};

function resolveMarkLine(
  panel: MonitorWatchPanel,
  formatMoney: (usd: number) => string,
): string | undefined {
  if (panel.markParts) {
    return formatMarkLine(panel.markParts, formatMoney);
  }
  return panel.markLine;
}

export function MonitorWatchList({ panels }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const { formatMoney } = useDisplayCurrency();
  const [busyId, setBusyId] = useState<string | null>(null);

  async function handleDelete(event: MouseEvent, tradeId: string, title: string) {
    event.preventDefault();
    event.stopPropagation();
    setBusyId(tradeId);
    const result = await deletePaperTradeWithUndo(tradeId);
    if (result.ok) {
      goToMonitorAfterDeleteFromRouter(router, result.title ?? title, pathname);
      if (!pathname.startsWith("/monitor/paper/")) {
        router.refresh();
      }
    }
    setBusyId(null);
  }

  return (
    <div className="monitor-watch-list" aria-label="Watch list">
      {panels.map((panel) => {
        const markLine = resolveMarkLine(panel, formatMoney);
        const content = (
          <>
            {panel.badge ? (
              <div className="monitor-watch-meta">
                <span className={`tag ${panel.tone}`}>{panel.badge}</span>
              </div>
            ) : null}
            <h3>{panel.title}</h3>
            <p>{panel.body}</p>
            {markLine ? <p className="micro watch-mark">{markLine}</p> : null}
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
