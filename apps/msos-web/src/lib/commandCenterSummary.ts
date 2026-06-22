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

const SOURCE_LABEL = "From your saved views";
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
      return { tag: "Held up", tone: "teal" };
    case "contradictory":
      return { tag: "Didn't hold", tone: "amber" };
    case "contaminated":
      return { tag: "Bad data", tone: "red" };
    case "not_judgeable":
      return { tag: "Unclear" };
    case "pending":
      return { tag: "Review due", tone: "amber" };
    default:
      return { tag: "Needs review", tone: "amber" };
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

function tableHasOwnerEmail(db: Database.Database): boolean {
  const cols = db.prepare("PRAGMA table_info(frozen_evaluations)").all() as { name: string }[];
  return cols.some((col) => col.name === "owner_email");
}

function ownerFilter(ownerEmail: string | null | undefined, hasOwnerColumn: boolean): { clause: string; params: string[] } {
  const owner = (ownerEmail ?? "").trim().toLowerCase();
  if (!owner || !hasOwnerColumn) {
    return { clause: "", params: [] };
  }
  return { clause: " AND fe.owner_email = ?", params: [owner] };
}

function countSnapshots(db: Database.Database, ownerEmail?: string | null): number {
  const hasOwnerColumn = tableHasOwnerEmail(db);
  const { clause, params } = ownerFilter(ownerEmail, hasOwnerColumn);
  const row = db
    .prepare(`SELECT COUNT(*) AS n FROM frozen_evaluations fe WHERE 1=1${clause}`)
    .get(...params) as { n: number };
  return Number(row.n) || 0;
}

function countPendingReviews(db: Database.Database, ownerEmail?: string | null): number {
  const hasOwnerColumn = tableHasOwnerEmail(db);
  const { clause, params } = ownerFilter(ownerEmail, hasOwnerColumn);
  const row = db
    .prepare(
      `
      SELECT COUNT(*) AS n
      FROM frozen_evaluations fe
      LEFT JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
      WHERE (sr.snapshot_id IS NULL OR sr.review_status = 'pending')${clause}
      `,
    )
    .get(...params) as { n: number };
  return Number(row.n) || 0;
}

function countCompletedReviews(db: Database.Database, ownerEmail?: string | null): number {
  const hasOwnerColumn = tableHasOwnerEmail(db);
  const { clause, params } = ownerFilter(ownerEmail, hasOwnerColumn);
  const row = db
    .prepare(
      `
      SELECT COUNT(*) AS n
      FROM snapshot_reviews sr
      INNER JOIN frozen_evaluations fe ON fe.id = sr.snapshot_id
      WHERE sr.review_status != 'pending'${clause}
      `,
    )
    .get(...params) as { n: number };
  return Number(row.n) || 0;
}

function listRecentSnapshots(db: Database.Database, limit: number, ownerEmail?: string | null): SnapshotRow[] {
  const hasOwnerColumn = tableHasOwnerEmail(db);
  const { clause, params } = ownerFilter(ownerEmail, hasOwnerColumn);
  return db
    .prepare(
      `
      SELECT fe.id, fe.created_at, fe.expiry, fe.summary_line,
             sr.review_status, sr.reviewed_at_utc
      FROM frozen_evaluations fe
      LEFT JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
      WHERE 1=1${clause}
      ORDER BY fe.created_at DESC
      LIMIT ?
      `,
    )
    .all(...params, limit) as SnapshotRow[];
}

function buildSummaryFromDb(db: Database.Database, ownerEmail?: string | null): CommandCenterSummary {
  const total = countSnapshots(db, ownerEmail);
  if (total === 0) {
    return {
      status: "empty",
      sourceLabel: SOURCE_LABEL,
      kpis: [
        { label: "Saved views", value: "0", sub: "Save a read in Strategy Lab" },
        { label: "Reviews due", value: "0", sub: "Nothing to review yet" },
        { label: "Reviews done", value: "0", sub: "Completed reviews appear here" },
      ],
      recentSnapshots: [],
      currentWork: [],
    };
  }

  const pending = countPendingReviews(db, ownerEmail);
  const completed = countCompletedReviews(db, ownerEmail);
  const rows = listRecentSnapshots(db, RECENT_LIMIT, ownerEmail);
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
      detail: `${row.expiry} · saved ${row.createdAt}`,
      tagTone: tone,
    };
  });

  return {
    status: "live",
    sourceLabel: SOURCE_LABEL,
    kpis: [
      {
        label: "Saved views",
        value: String(total),
        sub: "Captured market reads",
      },
      {
        label: "Reviews due",
        value: String(pending),
        sub: "Check whether your view held up",
        tone: pending > 0 ? "amber" : undefined,
      },
      {
        label: "Reviews done",
        value: String(completed),
        sub: "Completed reviews",
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
      { label: "Saved views", value: "—", sub: "History not connected" },
      { label: "Reviews due", value: "—", sub: "Unavailable" },
      { label: "Reviews done", value: "—", sub: "Unavailable" },
    ],
    recentSnapshots: [],
    currentWork: [],
  };
}

export function loadCommandCenterSummary(ownerEmail?: string | null): CommandCenterSummary {
  const dbPath = snapshotDbPath();
  if (!dbReadable(dbPath)) {
    return degradedSummary(`Snapshot database not readable at ${dbPath}`);
  }

  let db: Database.Database | undefined;
  try {
    db = openReadonlyDb(dbPath);
    return buildSummaryFromDb(db, ownerEmail);
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown snapshot read error";
    return degradedSummary(message);
  } finally {
    db?.close();
  }
}
