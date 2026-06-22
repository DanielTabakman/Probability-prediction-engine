import {
  loadCommandCenterSummary,
  type CommandCenterSummary,
  type CommandCenterSnapshotRow,
} from "@/lib/commandCenterSummary";
import { commandCenterCalibrationStrip } from "@/content/commandCenter";
import { getCurrentExpression, getCurrentThesis } from "@/lib/msosWorkflowStore";

export type MonitorWatchPanel = {
  id: string;
  title: string;
  body: string;
  tone: string;
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
  degradedReason?: string;
};

export type HistoryState = "observed" | "saved" | "simulated" | "reviewed";

export type HistoryEntry = {
  id: string;
  state: HistoryState;
  timestamp: string;
  title: string;
  detail: string;
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

const WORKFLOW_SOURCE = "Your workspace + saved views";

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

function workflowHistoryEntries(
  thesis: Awaited<ReturnType<typeof getCurrentThesis>>,
  expression: Awaited<ReturnType<typeof getCurrentExpression>>,
): HistoryEntry[] {
  const entries: HistoryEntry[] = [];
  if (thesis) {
    entries.push({
      id: `thesis-${thesis.id}`,
      state: thesis.lifecycle === "confirmed" ? "saved" : "observed",
      timestamp: formatTimestamp(thesis.updatedAt),
      title: `${thesis.instrument} thesis`,
      detail: `${thesis.horizonDays}d · ${thesis.referenceLabel} · ${thesis.trustLabel}`,
    });
  }
  if (expression) {
    entries.push({
      id: `expr-${expression.id}`,
      state: expression.lifecycle === "simulated" ? "simulated" : "saved",
      timestamp: formatTimestamp(expression.updatedAt),
      title: expression.planHeadline,
      detail: expression.planSummary,
    });
  }
  return entries;
}

function buildWatchPanels(
  thesis: Awaited<ReturnType<typeof getCurrentThesis>>,
  expression: Awaited<ReturnType<typeof getCurrentExpression>>,
  summary: CommandCenterSummary,
): MonitorWatchPanel[] {
  const panels: MonitorWatchPanel[] = [];
  if (thesis) {
    panels.push({
      id: "A",
      title: `${thesis.instrument} thesis`,
      body: `${thesis.lifecycle} · ${thesis.horizonDays}d horizon · ${thesis.referenceLabel}`,
      tone: thesis.lifecycle === "confirmed" ? "teal" : "amber",
    });
  }
  if (expression) {
    panels.push({
      id: "B",
      title: expression.planHeadline,
      body: `${expression.lifecycle} expression · ${expression.familyId}`,
      tone: expression.lifecycle === "simulated" ? "teal" : "amber",
    });
  }
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
        body: "Reviews recorded on saved market reads.",
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

function healthFromSummary(summary: CommandCenterSummary): { pct: number; label: string } {
  if (summary.status !== "live") {
    return { pct: 0, label: "Waiting for saved reads" };
  }
  const totalKpi = summary.kpis.find((k) => k.label === "Saved views");
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

export async function loadMonitorFeed(ownerEmail: string | null): Promise<MonitorFeed> {
  const summary = loadCommandCenterSummary(ownerEmail);
  const email = ownerEmail ?? "";
  const [thesis, expression] = await Promise.all([
    getCurrentThesis(email),
    getCurrentExpression(email),
  ]);

  if (summary.status === "degraded") {
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
    };
  }

  const watchPanels = buildWatchPanels(thesis, expression, summary);
  const alerts = buildAlerts(summary);
  const { pct, label } = healthFromSummary(summary);
  const hasWorkflow = Boolean(thesis || expression);
  const hasSnapshots = summary.status === "live" && summary.recentSnapshots.length > 0;

  return {
    status: hasWorkflow || hasSnapshots ? "live" : "empty",
    sourceLabel: WORKFLOW_SOURCE,
    heroTitle: hasWorkflow ? "Your open ideas" : "Monitor",
    heroSubtitle: hasSnapshots
      ? "Watching your saved views and paper trades."
      : "Save a view in Strategy Lab to start building history.",
    healthPct: pct,
    healthLabel: label,
    watchPanels,
    alerts,
  };
}

export async function loadHistoryFeed(ownerEmail: string | null): Promise<HistoryFeed> {
  const summary = loadCommandCenterSummary(ownerEmail);
  const email = ownerEmail ?? "";
  const [thesis, expression] = await Promise.all([
    getCurrentThesis(email),
    getCurrentExpression(email),
  ]);

  if (summary.status === "degraded") {
    return {
      status: "degraded",
      sourceLabel: WORKFLOW_SOURCE,
      intro: "Saved history isn't available right now.",
      entries: [],
      degradedReason: summary.degradedReason,
    };
  }

  const entries = [
    ...workflowHistoryEntries(thesis, expression),
    ...snapshotHistoryEntries(summary.recentSnapshots),
  ].sort((a, b) => b.timestamp.localeCompare(a.timestamp));

  return {
    status: entries.length > 0 ? "live" : "empty",
    sourceLabel: WORKFLOW_SOURCE,
    intro: "From first look → saved view → paper trade → review. Live fills appear when connected.",
    entries,
  };
}

export function buildCalibrationStrip(summary: CommandCenterSummary): CalibrationStrip {
  if (summary.status === "degraded") {
    return {
      title: commandCenterCalibrationStrip.title,
      body: commandCenterCalibrationStrip.bodyDegraded,
      cta: commandCenterCalibrationStrip.cta,
      href: commandCenterCalibrationStrip.href,
    };
  }
  const pendingKpi = summary.kpis.find((k) => k.label === "Reviews due");
  const pending = Number(pendingKpi?.value ?? "0");
  if (pending > 0) {
    return {
      title: commandCenterCalibrationStrip.title,
      body: commandCenterCalibrationStrip.bodyPending(pending),
      cta: commandCenterCalibrationStrip.cta,
      href: commandCenterCalibrationStrip.href,
    };
  }
  return {
    title: commandCenterCalibrationStrip.title,
    body: commandCenterCalibrationStrip.bodyDefault,
    cta: commandCenterCalibrationStrip.cta,
    href: commandCenterCalibrationStrip.href,
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
