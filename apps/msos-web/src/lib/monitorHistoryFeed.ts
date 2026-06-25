import {
  loadCommandCenterSummary,
  type CommandCenterSummary,
  type CommandCenterSnapshotRow,
} from "@/lib/commandCenterSummary";
import type { StoredExpression } from "@/lib/msosWorkflowStore";
import type { PaperTradeStatus } from "@/lib/expressionPersistence";
import {
  effectivePaperTradeStatus,
  getCurrentThesis,
  listPaperTrades,
} from "@/lib/msosWorkflowStore";
import { fetchDisplayPayload, formatUsd } from "@/lib/ppeDisplayPayload";

export type MonitorWatchPanel = {
  id: string;
  title: string;
  body: string;
  tone: string;
  markLine?: string;
  href?: string;
  tradeId?: string;
  status?: PaperTradeStatus;
};

export type PaperTradeSummary = {
  id: string;
  title: string;
  status: PaperTradeStatus;
};

export type MonitorAlert = {
  title: string;
  body: string;
  tone: string;
};

export type MonitorFeed = {
  status: "live" | "empty" | "degraded";
  sourceLabel: string;
  heroTitle: string;
  heroSubtitle: string;
  healthPct: number;
  healthLabel: string;
  watchPanels: MonitorWatchPanel[];
  alerts: MonitorAlert[];
  paperTrades: PaperTradeSummary[];
  manageEnabled: boolean;
  degradedReason?: string;
};

export type HistoryState = "observed" | "saved" | "simulated" | "reviewed";

export type HistoryEntry = {
  id: string;
  state: HistoryState;
  timestamp: string;
  title: string;
  detail: string;
  href?: string;
  tradeId?: string;
  statusTag?: string;
  paperTradeStatus?: PaperTradeStatus;
};

export type HistoryFeed = {
  status: "live" | "empty" | "degraded";
  sourceLabel: string;
  intro: string;
  entries: HistoryEntry[];
  degradedReason?: string;
};

export type CalibrationStrip = {
  title: string;
  body: string;
  cta: string;
  href: string;
};

const WORKFLOW_SOURCE = "Your workspace + saved snapshots";

function reviewState(row: CommandCenterSnapshotRow): HistoryState {
  const status = (row.reviewStatus ?? "").trim().toLowerCase();
  if (!status || status === "pending") return "observed";
  return "reviewed";
}

function formatTimestamp(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return "—";
  const parsed = Date.parse(trimmed);
  if (Number.isNaN(parsed)) return trimmed;
  return new Date(parsed).toISOString().slice(0, 16).replace("T", " ");
}

function snapshotHistoryEntries(rows: CommandCenterSnapshotRow[]): HistoryEntry[] {
  return rows.map((row) => {
    const state = reviewState(row);
    const tag = state === "reviewed" ? "Reviewed" : "Review due";
    return {
      id: `snap-${row.snapshotId}`,
      state,
      timestamp: formatTimestamp(row.createdAt),
      title: row.summaryLine,
      detail: `${row.expiry} · ${tag}`,
    };
  });
}

function statusLabel(status: PaperTradeStatus): string {
  if (status === "closed") return "Closed";
  if (status === "expired") return "Expired";
  return "Open";
}

function paperTradeHistoryEntries(trades: StoredExpression[]): HistoryEntry[] {
  return trades.map((expression) => {
    const status = effectivePaperTradeStatus(expression);
    const expiry = expression.expiryDate?.trim();
    const instrument = expression.instrument?.trim();
    const legs = expression.legs.length;
    const detailParts = [
      expression.planSummary,
      `${statusLabel(status)}`,
      expiry ? `exp ${expiry}` : null,
      instrument ? instrument : null,
      legs > 0 ? `${legs} leg${legs === 1 ? "" : "s"}` : null,
    ].filter(Boolean);
    return {
      id: `paper-${expression.id}`,
      state: "simulated" as HistoryState,
      timestamp: formatTimestamp(expression.savedAt ?? expression.updatedAt),
      title: expression.planHeadline,
      detail: detailParts.join(" · "),
      href: `/monitor/paper/${expression.id}`,
      tradeId: expression.id,
      statusTag: statusLabel(status),
      paperTradeStatus: status,
    };
  });
}

function workflowHistoryEntries(
  thesis: Awaited<ReturnType<typeof getCurrentThesis>>,
  paperTrades: StoredExpression[],
): HistoryEntry[] {
  const entries: HistoryEntry[] = paperTradeHistoryEntries(paperTrades);
  if (thesis && thesis.lifecycle === "confirmed") {
    const hasThesisEntry = entries.some((row) => row.id === `thesis-${thesis.id}`);
    if (!hasThesisEntry) {
      entries.push({
        id: `thesis-${thesis.id}`,
        state: "saved",
        timestamp: formatTimestamp(thesis.updatedAt),
        title: `${thesis.instrument} thesis`,
        detail: `${thesis.horizonDays}d · ${thesis.referenceLabel} · ${thesis.trustLabel}`,
      });
    }
  }
  return entries;
}

function markLineForTrade(
  trade: StoredExpression,
  currentSpotUsd: number | null,
  asOfUtc?: string,
): string | undefined {
  const saved = trade.markAtSave;
  if (!saved?.spotUsd && currentSpotUsd == null) {
    return undefined;
  }
  const savedSpot = saved?.spotUsd;
  const parts: string[] = [];
  if (typeof savedSpot === "number" && currentSpotUsd != null) {
    parts.push(`Spot ${formatUsd(savedSpot)} → ${formatUsd(currentSpotUsd)}`);
  } else if (typeof savedSpot === "number") {
    parts.push(`Saved at ${formatUsd(savedSpot)}`);
  } else if (currentSpotUsd != null) {
    parts.push(`Spot now ${formatUsd(currentSpotUsd)}`);
  }
  if (typeof saved?.maxLossUsd === "number") {
    parts.push(`max loss ${formatUsd(Math.abs(saved.maxLossUsd))}`);
  }
  if (asOfUtc?.trim()) {
    parts.push(`as of ${formatTimestamp(asOfUtc)} UTC`);
  }
  return parts.length > 0 ? parts.join(" · ") : undefined;
}

function buildWatchPanels(
  thesis: Awaited<ReturnType<typeof getCurrentThesis>>,
  paperTrades: StoredExpression[],
  summary: CommandCenterSummary,
  currentSpotUsd: number | null,
  marketAsOfUtc?: string,
): MonitorWatchPanel[] {
  const panels: MonitorWatchPanel[] = [];
  if (thesis) {
    panels.push({
      id: "thesis",
      title: `${thesis.instrument} thesis`,
      body: `${thesis.lifecycle} · ${thesis.horizonDays}d horizon · ${thesis.referenceLabel}`,
      tone: thesis.lifecycle === "confirmed" ? "teal" : "amber",
    });
  }
  paperTrades.forEach((expression) => {
    const status = effectivePaperTradeStatus(expression);
    const expiry = expression.expiryDate?.trim();
    panels.push({
      id: `paper-${expression.id}`,
      title: expression.planHeadline,
      body: [
        statusLabel(status),
        `${expression.legs.length} leg${expression.legs.length === 1 ? "" : "s"}`,
        expiry ? `exp ${expiry}` : null,
        expression.instrument?.trim() ?? null,
      ]
        .filter(Boolean)
        .join(" · "),
      tone: status === "open" ? "teal" : status === "closed" ? "muted" : "amber",
      markLine: markLineForTrade(expression, currentSpotUsd, marketAsOfUtc),
      href: `/monitor/paper/${expression.id}`,
      tradeId: expression.id,
      status,
    });
  });
  if (summary.status === "live" && summary.recentSnapshots.length > 0) {
    const latest = summary.recentSnapshots[0];
    panels.push({
      id: "C",
      title: "Latest saved read",
      body: `${latest.summaryLine} · ${latest.expiry}`,
      tone: "teal",
    });
  }
  if (panels.length === 0) {
    panels.push({
      id: "—",
      title: "No active watch items",
      body: "Save a view in Strategy Lab to start monitoring.",
      tone: "muted",
    });
  }
  return panels;
}

function buildAlerts(summary: CommandCenterSummary): MonitorAlert[] {
  const alerts: MonitorAlert[] = [];
  if (summary.status === "live") {
    const pendingKpi = summary.kpis.find((k) => k.label === "Reviews due");
    const pending = Number(pendingKpi?.value ?? "0");
    if (pending > 0) {
      alerts.push({
        title: `${pending} review${pending === 1 ? "" : "s"} due`,
        body: "Check whether your saved views still match the market — not trade advice.",
        tone: "amber",
      });
    }
    const completedKpi = summary.kpis.find((k) => k.label === "Reviews done");
    const completed = Number(completedKpi?.value ?? "0");
    if (completed > 0) {
      alerts.push({
        title: `${completed} review${completed === 1 ? "" : "s"} complete`,
        body: "Post-mortems recorded on saved market reads.",
        tone: "teal",
      });
    }
  }
  if (alerts.length === 0) {
    alerts.push({
      title: "Monitoring ready",
      body: "Your workspace is connected — no alerts right now.",
      tone: "teal",
    });
  }
  return alerts;
}

function healthFromSummary(
  summary: CommandCenterSummary,
  hasPaperTrades = false,
): { pct: number; label: string } {
  if (summary.status !== "live") {
    if (hasPaperTrades) {
      return { pct: 50, label: "Paper trades saved — snapshot reviews offline" };
    }
    return { pct: 0, label: "Waiting for saved reads" };
  }
  const totalKpi = summary.kpis.find((k) => k.label === "Saved snapshots");
  const pendingKpi = summary.kpis.find((k) => k.label === "Reviews due");
  const total = Number(totalKpi?.value ?? "0");
  const pending = Number(pendingKpi?.value ?? "0");
  if (total === 0) {
    return { pct: 25, label: "Save a read in Strategy Lab" };
  }
  const reviewed = Math.max(0, total - pending);
  const pct = Math.round((reviewed / total) * 100);
  return {
    pct: Math.max(10, pct),
    label: `${reviewed}/${total} reads reviewed`,
  };
}

function healthFromPaperTrades(trades: StoredExpression[]): { pct: number; label: string } {
  const open = trades.filter((row) => effectivePaperTradeStatus(row) === "open").length;
  const closed = trades.filter((row) => effectivePaperTradeStatus(row) === "closed").length;
  const expired = trades.filter((row) => effectivePaperTradeStatus(row) === "expired").length;
  const total = trades.length;
  const pct = open > 0 ? 70 : closed > 0 ? 45 : 30;
  const parts = [`${open} open`];
  if (closed) parts.push(`${closed} closed`);
  if (expired) parts.push(`${expired} expired`);
  return {
    pct,
    label: `${parts.join(" · ")} · ${total} saved`,
  };
}

export async function loadMonitorFeed(ownerEmail: string | null): Promise<MonitorFeed> {
  const summary = loadCommandCenterSummary(ownerEmail);
  const email = ownerEmail ?? "";
  const [thesis, paperTrades, display] = await Promise.all([
    getCurrentThesis(email),
    listPaperTrades(email),
    fetchDisplayPayload(),
  ]);
  const currentSpotUsd = display?.spot_usd ?? null;
  const marketAsOfUtc = display?.as_of_utc;

  const hasPaperTrades = paperTrades.length > 0;
  const hasWorkflow = Boolean(thesis || hasPaperTrades);

  if (summary.status === "degraded" && !hasWorkflow) {
    return {
      status: "degraded",
      sourceLabel: WORKFLOW_SOURCE,
      heroTitle: "Monitor unavailable",
      heroSubtitle: "Saved history isn't connected yet. Strategy Lab still works.",
      healthPct: 0,
      healthLabel: "Offline",
      watchPanels: [
        {
          id: "!",
          title: "History offline",
          body: "We're connecting saved market reads. Live options in Strategy Lab still work.",
          tone: "red",
        },
      ],
      alerts: [
        {
          title: "Saved reads unavailable",
          body: "Try again later or continue in Strategy Lab.",
          tone: "red",
        },
      ],
      degradedReason: summary.degradedReason,
      paperTrades: [],
      manageEnabled: false,
    };
  }

  const paperTradeSummaries: PaperTradeSummary[] = paperTrades.map((trade) => ({
    id: trade.id,
    title: trade.planHeadline,
    status: effectivePaperTradeStatus(trade),
  }));
  const watchPanels = buildWatchPanels(
    thesis,
    paperTrades,
    summary,
    currentSpotUsd,
    marketAsOfUtc,
  );
  const alerts = buildAlerts(summary);
  const health = hasPaperTrades
    ? healthFromPaperTrades(paperTrades)
    : healthFromSummary(summary, hasPaperTrades);
  const hasSnapshots = summary.status === "live" && summary.recentSnapshots.length > 0;

  return {
    status: hasWorkflow || hasSnapshots ? "live" : "empty",
    sourceLabel: WORKFLOW_SOURCE,
    heroTitle: hasPaperTrades ? "Paper trade watch" : hasWorkflow ? "Thesis watch" : "Monitoring workspace",
    heroSubtitle: hasPaperTrades
      ? `${paperTrades.length} saved paper trade${paperTrades.length === 1 ? "" : "s"} — marks refresh when Deribit data is online.`
      : hasSnapshots
        ? "Watching your saved views."
        : "Save a paper trade in Strategy Lab to start building history.",
    healthPct: health.pct,
    healthLabel: health.label,
    watchPanels,
    alerts,
    paperTrades: paperTradeSummaries,
    manageEnabled: hasPaperTrades,
  };
}

export async function loadHistoryFeed(ownerEmail: string | null): Promise<HistoryFeed> {
  const summary = loadCommandCenterSummary(ownerEmail);
  const email = ownerEmail ?? "";
  const [thesis, paperTrades] = await Promise.all([getCurrentThesis(email), listPaperTrades(email)]);

  const hasPaperTrades = paperTrades.length > 0;
  if (summary.status === "degraded" && !hasPaperTrades && !thesis) {
    return {
      status: "degraded",
      sourceLabel: WORKFLOW_SOURCE,
      intro: "Saved history isn't available right now.",
      entries: [],
      degradedReason: summary.degradedReason,
    };
  }

  const entries = [
    ...workflowHistoryEntries(thesis, paperTrades),
    ...(summary.status === "live" ? snapshotHistoryEntries(summary.recentSnapshots) : []),
  ].sort((a, b) => b.timestamp.localeCompare(a.timestamp));

  return {
    status: entries.length > 0 ? "live" : "empty",
    sourceLabel: WORKFLOW_SOURCE,
    intro: hasPaperTrades
      ? "Paper trades and saved views in your workspace — newest first."
      : "From first look → saved view → paper trade → review. Live fills appear when connected.",
    entries,
    degradedReason: summary.status === "degraded" ? summary.degradedReason : undefined,
  };
}

export function buildCalibrationStrip(summary: CommandCenterSummary): CalibrationStrip {
  if (summary.status === "degraded") {
    return {
      title: "Track your accuracy",
      body: "Saved history isn't connected yet — Strategy Lab live data still works.",
      cta: "Open monitor",
      href: "/monitor",
    };
  }
  const pendingKpi = summary.kpis.find((k) => k.label === "Reviews due");
  const pending = Number(pendingKpi?.value ?? "0");
  if (pending > 0) {
    return {
      title: "Track your accuracy",
      body: `${pending} saved view${pending === 1 ? "" : "s"} ready for a post-mortem.`,
      cta: "Open monitor",
      href: "/monitor",
    };
  }
  return {
    title: "Track your accuracy",
    body: "Compare what you thought would happen with what actually happened — paper trading only for now.",
    cta: "Open monitor",
    href: "/monitor",
  };
}

export function buildReviewEvents(summary: CommandCenterSummary): MonitorAlert[] {
  if (summary.status !== "live" || summary.recentSnapshots.length === 0) {
    return [];
  }
  return summary.recentSnapshots.slice(0, 4).map((row) => {
    const pending = !row.reviewStatus || row.reviewStatus === "pending";
    return {
      title: row.summaryLine,
      body: pending
        ? `Review due · saved ${formatTimestamp(row.createdAt)}`
        : `Reviewed · ${formatTimestamp(row.reviewedAtUtc ?? row.createdAt)}`,
      tone: pending ? "amber" : "teal",
    };
  });
}
