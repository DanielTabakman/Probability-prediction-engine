import { accessSync, constants } from "fs";
import path from "path";

import Database from "better-sqlite3";

export type CommandCenterSummaryKpi = {
  label: string;
  value: string;
  sub: string;
  tone?: string;
};

export type CommandCenterSnapshotRow = {
  snapshotId: string;
  createdAt: string;
  expiry: string;
  summaryLine: string;
  reviewStatus: string | null;
  reviewedAtUtc: string | null;
};

export type CommandCenterWorkItem = {
  snapshotId: string;
  name: string;
  tag: string;
  detail: string;
  tagTone?: string;
};

export type CommandCenterSummary = {
  status: "live" | "empty" | "degraded";
  sourceLabel: string;
  degradedReason?: string;
  kpis: CommandCenterSummaryKpi[];
  recentSnapshots: CommandCenterSnapshotRow[];
  currentWork: CommandCenterWorkItem[];
};

const SOURCE_LABEL = "From PPE snapshots";
const RECENT_LIMIT = 10;

type SnapshotRow = {
  id: string;
  created_at: string;
  expiry: string;
  summary_line: string;
  review_status: string | null;
  reviewed_at_utc: string | null;
};

function reviewTag(status: string | null): { tag: string; tone?: string } {
  switch ((status ?? "").trim().toLowerCase()) {
    case "supportive":
      return { tag: "Review: supportive", tone: "teal" };
    case "contradictory":
      return { tag: "Review: contradictory", tone: "amber" };
    case "contaminated":
      return { tag: "Review: contaminated", tone: "red" };
    case "not_judgeable":
      return { tag: "Review: not judgeable" };
    case "pending":
      return { tag: "Review pending", tone: "amber" };
    default:
      return { tag: "Awaiting review", tone: "amber" };
  }
}

export function snapshotDbPath(): string {
  const explicit = process.env.PPE_SNAPSHOT_DB_PATH?.trim();
  if (explicit) return explicit;
  return path.join(process.cwd(), "..", "..", "data", "ppe_frozen_evaluations.sqlite3");
}

function dbReadable(filePath: string): boolean {
  try {
    accessSync(filePath, constants.R_OK);
    return true;
  } catch {
    return false;
  }
}

function openReadonlyDb(filePath: string): Database.Database {
  return new Database(filePath, { readonly: true, fileMustExist: true });
}

function countSnapshots(db: Database.Database): number {
  const row = db.prepare("SELECT COUNT(*) AS n FROM frozen_evaluations").get() as { n: number };
  return Number(row.n) || 0;
}

function countPendingReviews(db: Database.Database): number {
  const row = db
    .prepare(
      `
      SELECT COUNT(*) AS n
      FROM frozen_evaluations fe
      LEFT JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
      WHERE sr.snapshot_id IS NULL OR sr.review_status = 'pending'
      `,
    )
    .get() as { n: number };
  return Number(row.n) || 0;
}

function countCompletedReviews(db: Database.Database): number {
  const row = db
    .prepare(
      `
      SELECT COUNT(*) AS n
      FROM snapshot_reviews sr
      WHERE sr.review_status != 'pending'
      `,
    )
    .get() as { n: number };
  return Number(row.n) || 0;
}

function listRecentSnapshots(db: Database.Database, limit: number): SnapshotRow[] {
  return db
    .prepare(
      `
      SELECT fe.id, fe.created_at, fe.expiry, fe.summary_line,
             sr.review_status, sr.reviewed_at_utc
      FROM frozen_evaluations fe
      LEFT JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
      ORDER BY fe.created_at DESC
      LIMIT ?
      `,
    )
    .all(limit) as SnapshotRow[];
}

function buildSummaryFromDb(db: Database.Database): CommandCenterSummary {
  const total = countSnapshots(db);
  if (total === 0) {
    return {
      status: "empty",
      sourceLabel: SOURCE_LABEL,
      kpis: [
        { label: "Frozen snapshots", value: "0", sub: "Freeze evaluations in Strategy Lab" },
        { label: "Reviews pending", value: "0", sub: "No snapshot rows yet" },
        { label: "Reviews completed", value: "0", sub: "Outcome reviews appear here" },
      ],
      recentSnapshots: [],
      currentWork: [],
    };
  }

  const pending = countPendingReviews(db);
  const completed = countCompletedReviews(db);
  const rows = listRecentSnapshots(db, RECENT_LIMIT);
  const recentSnapshots: CommandCenterSnapshotRow[] = rows.map((row) => ({
    snapshotId: row.id,
    createdAt: row.created_at,
    expiry: row.expiry,
    summaryLine: row.summary_line,
    reviewStatus: row.review_status,
    reviewedAtUtc: row.reviewed_at_utc,
  }));

  const currentWork: CommandCenterWorkItem[] = recentSnapshots.map((row) => {
    const { tag, tone } = reviewTag(row.reviewStatus);
    return {
      snapshotId: row.snapshotId,
      name: row.summaryLine,
      tag,
      detail: `${row.expiry} · frozen ${row.createdAt}`,
      tagTone: tone,
    };
  });

  return {
    status: "live",
    sourceLabel: SOURCE_LABEL,
    kpis: [
      {
        label: "Frozen snapshots",
        value: String(total),
        sub: "PPE implied-lab freezes",
      },
      {
        label: "Reviews pending",
        value: String(pending),
        sub: "Awaiting outcome review",
        tone: pending > 0 ? "amber" : undefined,
      },
      {
        label: "Reviews completed",
        value: String(completed),
        sub: "Non-pending review statuses",
        tone: completed > 0 ? "teal" : undefined,
      },
    ],
    recentSnapshots,
    currentWork,
  };
}

export function degradedSummary(reason: string): CommandCenterSummary {
  return {
    status: "degraded",
    sourceLabel: SOURCE_LABEL,
    degradedReason: reason,
    kpis: [
      { label: "Frozen snapshots", value: "—", sub: "Snapshot database unavailable" },
      { label: "Reviews pending", value: "—", sub: "Read-only feed offline" },
      { label: "Reviews completed", value: "—", sub: "Check PPE_SNAPSHOT_DB_PATH mount" },
    ],
    recentSnapshots: [],
    currentWork: [],
  };
}

export function loadCommandCenterSummary(): CommandCenterSummary {
  const dbPath = snapshotDbPath();
  if (!dbReadable(dbPath)) {
    return degradedSummary(`Snapshot database not readable at ${dbPath}`);
  }

  let db: Database.Database | undefined;
  try {
    db = openReadonlyDb(dbPath);
    return buildSummaryFromDb(db);
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown snapshot read error";
    return degradedSummary(message);
  } finally {
    db?.close();
  }
}
