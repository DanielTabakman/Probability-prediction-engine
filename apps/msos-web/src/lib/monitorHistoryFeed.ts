import {
  loadCommandCenterSummary,
  type CommandCenterSummary,
  type CommandCenterSnapshotRow,
} from "@/lib/commandCenterSummary";
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

const WORKFLOW_SOURCE = "From MSOS workflow + PPE snapshots";

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
    const tag = state === "reviewed" ? "Review recorded" : "Awaiting review";
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
      title: "Latest PPE freeze",
      body: `${latest.summaryLine} · ${latest.expiry}`,
      tone: "teal",
    });
  }
  if (panels.length === 0) {
    panels.push({
      id: "—",
      title: "No active watch items",
      body: "Create a thesis in Strategy Lab or freeze an evaluation to populate monitoring.",
      tone: "muted",
    });
  }
  return panels;
}

function buildAlerts(summary: CommandCenterSummary): MonitorAlert[] {
  const alerts: MonitorAlert[] = [];
  if (summary.status === "live") {
    const pendingKpi = summary.kpis.find((k) => k.label === "Reviews pending");
    const pending = Number(pendingKpi?.value ?? "0");
    if (pending > 0) {
      alerts.push({
        title: `${pending} review${pending === 1 ? "" : "s"} due`,
        body: "Outcome reviews pending on frozen PPE snapshots — not trade advice.",
        tone: "amber",
      });
    }
    const completedKpi = summary.kpis.find((k) => k.label === "Reviews completed");
    const completed = Number(completedKpi?.value ?? "0");
    if (completed > 0) {
      alerts.push({
        title: `${completed} review${completed === 1 ? "" : "s"} recorded`,
        body: "Recorded snapshot reviews in the PPE store.",
        tone: "teal",
      });
    }
  }
  if (alerts.length === 0) {
    alerts.push({
      title: "Monitoring ready",
      body: "Workflow and snapshot feeds connected — no alerts raised.",
      tone: "teal",
    });
  }
  return alerts;
}

function healthFromSummary(summary: CommandCenterSummary): { pct: number; label: string } {
  if (summary.status !== "live") {
    return { pct: 0, label: "Awaiting workflow + snapshot data" };
  }
  const totalKpi = summary.kpis.find((k) => k.label === "Frozen snapshots");
  const pendingKpi = summary.kpis.find((k) => k.label === "Reviews pending");
  const total = Number(totalKpi?.value ?? "0");
  const pending = Number(pendingKpi?.value ?? "0");
  if (total === 0) {
    return { pct: 25, label: "Snapshots empty — freeze in Strategy Lab" };
  }
  const reviewed = Math.max(0, total - pending);
  const pct = Math.round((reviewed / total) * 100);
  return {
    pct: Math.max(10, pct),
    label: `${reviewed}/${total} snapshots reviewed`,
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
      heroTitle: "Monitor feed unavailable",
      heroSubtitle: summary.degradedReason ?? "Snapshot database not readable.",
      healthPct: 0,
      healthLabel: "Degraded",
      watchPanels: [
        {
          id: "!",
          title: "Snapshot feed offline",
          body: "Check PPE_SNAPSHOT_DB_PATH mount on msos_web.",
          tone: "red",
        },
      ],
      alerts: [
        {
          title: "Read-only snapshot mount required",
          body: summary.degradedReason ?? "Database unavailable",
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
    heroTitle: hasWorkflow ? "Thesis & expression watch" : "Monitoring workspace",
    heroSubtitle: hasSnapshots
      ? "Live MSOS workflow + PPE snapshot review metadata (scoped to you)."
      : "MSOS workflow connected — freeze evaluations to add snapshot watch.",
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
      intro: summary.degradedReason ?? "Snapshot database unavailable.",
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
    intro: "Observed → saved → simulated → reviewed — Executed stays empty until live routing ships.",
    entries,
  };
}

export function buildCalibrationStrip(summary: CommandCenterSummary): CalibrationStrip {
  if (summary.status === "degraded") {
    return {
      title: "Calibration loop",
      body: "Snapshot feed unavailable — connect read-only PPE frozen evaluations to enable review hooks.",
      cta: "Open monitor",
      href: "/monitor",
    };
  }
  const pendingKpi = summary.kpis.find((k) => k.label === "Reviews pending");
  const pending = Number(pendingKpi?.value ?? "0");
  if (pending > 0) {
    return {
      title: "Calibration loop",
      body: `${pending} outcome review${pending === 1 ? "" : "s"} due on frozen snapshots — observed vs saved vs simulated.`,
      cta: "Open monitor",
      href: "/monitor",
    };
  }
  return {
    title: "Calibration loop",
    body: "Review observed vs saved vs simulated theses — executed count stays zero until live routing ships.",
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
        ? `Review due · frozen ${formatTimestamp(row.createdAt)}`
        : `Review: ${row.reviewStatus} · ${formatTimestamp(row.reviewedAtUtc ?? row.createdAt)}`,
      tone: pending ? "amber" : "teal",
    };
  });
}
