import { accessSync, constants } from "fs";
import { randomUUID } from "crypto";

import Database from "better-sqlite3";

import { snapshotDbPath } from "@/lib/commandCenterSummary";

export * from "@/lib/snapshotReviewShared";

import {
  isValidReviewStatus,
  reviewHorizonRefFromFrozen,
  REVIEW_STATUSES,
  type ReviewStatus,
  type SnapshotReviewRow,
} from "@/lib/snapshotReviewShared";

export type SnapshotDetail = {
  snapshotId: string;
  createdAt: string;
  expiry: string;
  summaryLine: string;
  record: Record<string, unknown>;
  review: SnapshotReviewRow | null;
};

function dbReadable(filePath: string): boolean {
  try {
    accessSync(filePath, constants.R_OK | constants.W_OK);
    return true;
  } catch {
    try {
      accessSync(filePath, constants.R_OK);
      return true;
    } catch {
      return false;
    }
  }
}

function openDb(filePath: string, readonly = false): Database.Database {
  return new Database(filePath, { readonly, fileMustExist: true });
}

function tableHasOwnerEmail(db: Database.Database): boolean {
  const cols = db.prepare("PRAGMA table_info(frozen_evaluations)").all() as { name: string }[];
  return cols.some((col) => col.name === "owner_email");
}

function normalizeOwnerEmail(raw: string | null | undefined): string | null {
  const email = (raw ?? "").trim().toLowerCase();
  return email || null;
}

function ownerMatches(
  rowOwner: string | null | undefined,
  requestOwner: string | null | undefined,
  hasOwnerColumn: boolean,
): boolean {
  if (!hasOwnerColumn) return true;
  const expected = normalizeOwnerEmail(requestOwner);
  if (!expected) return true;
  const actual = normalizeOwnerEmail(rowOwner);
  if (!actual) return true;
  return actual === expected;
}

function utcIsoNow(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function mapReviewRow(row: {
  id: string;
  snapshot_id: string;
  review_status: string;
  outcome_notes: string | null;
  reviewed_at_utc: string;
  review_horizon_ref: string | null;
  paper_tag: string | null;
}): SnapshotReviewRow {
  return {
    id: row.id,
    snapshotId: row.snapshot_id,
    reviewStatus: row.review_status as ReviewStatus,
    outcomeNotes: row.outcome_notes,
    reviewedAtUtc: row.reviewed_at_utc,
    reviewHorizonRef: row.review_horizon_ref,
    paperTag: row.paper_tag,
  };
}

type FrozenRow = {
  id: string;
  created_at: string;
  expiry: string;
  summary_line: string;
  record_json: string;
  owner_email?: string | null;
};

export function loadSnapshotDetail(
  snapshotId: string,
  ownerEmail?: string | null,
): SnapshotDetail | null {
  const dbPath = snapshotDbPath();
  if (!dbReadable(dbPath)) return null;

  let db: Database.Database | undefined;
  try {
    db = openDb(dbPath, true);
    const hasOwnerColumn = tableHasOwnerEmail(db);
    const cols = hasOwnerColumn ? ", fe.owner_email" : "";
    const row = db
      .prepare(
        `SELECT fe.id, fe.created_at, fe.expiry, fe.summary_line, fe.record_json${cols}
         FROM frozen_evaluations fe WHERE fe.id = ?`,
      )
      .get(snapshotId) as FrozenRow | undefined;
    if (!row) return null;
    if (!ownerMatches(row.owner_email, ownerEmail, hasOwnerColumn)) return null;

    let record: Record<string, unknown> = {};
    try {
      record = JSON.parse(row.record_json) as Record<string, unknown>;
    } catch {
      record = {};
    }

    const reviewRow = db
      .prepare(
        `SELECT id, snapshot_id, review_status, outcome_notes, reviewed_at_utc,
                review_horizon_ref, paper_tag
         FROM snapshot_reviews WHERE snapshot_id = ?`,
      )
      .get(snapshotId) as
      | {
          id: string;
          snapshot_id: string;
          review_status: string;
          outcome_notes: string | null;
          reviewed_at_utc: string;
          review_horizon_ref: string | null;
          paper_tag: string | null;
        }
      | undefined;

    return {
      snapshotId: row.id,
      createdAt: row.created_at,
      expiry: row.expiry,
      summaryLine: row.summary_line,
      record,
      review: reviewRow ? mapReviewRow(reviewRow) : null,
    };
  } catch {
    return null;
  } finally {
    db?.close();
  }
}

export type UpsertReviewResult =
  | { ok: true; review: SnapshotReviewRow }
  | { ok: false; error: string; httpStatus: number };

export function upsertSnapshotReview(input: {
  snapshotId: string;
  reviewStatus: string;
  outcomeNotes?: string | null;
  paperTag?: string | null;
  ownerEmail?: string | null;
}): UpsertReviewResult {
  const status = input.reviewStatus.trim();
  if (!isValidReviewStatus(status)) {
    return {
      ok: false,
      error: `invalid review_status; expected one of ${REVIEW_STATUSES.join(", ")}`,
      httpStatus: 400,
    };
  }

  const dbPath = snapshotDbPath();
  if (!dbReadable(dbPath)) {
    return { ok: false, error: "snapshot database unavailable", httpStatus: 503 };
  }

  let db: Database.Database | undefined;
  try {
    db = openDb(dbPath, false);
    db.pragma("foreign_keys = ON");

    const hasOwnerColumn = tableHasOwnerEmail(db);
    const cols = hasOwnerColumn ? ", owner_email" : "";
    const row = db
      .prepare(`SELECT id, record_json${cols} FROM frozen_evaluations WHERE id = ?`)
      .get(input.snapshotId) as
      | { id: string; record_json: string; owner_email?: string | null }
      | undefined;

    if (!row) {
      return { ok: false, error: "snapshot not found", httpStatus: 404 };
    }
    if (!ownerMatches(row.owner_email, input.ownerEmail, hasOwnerColumn)) {
      return { ok: false, error: "snapshot not found", httpStatus: 404 };
    }

    let record: Record<string, unknown> = {};
    try {
      record = JSON.parse(row.record_json) as Record<string, unknown>;
    } catch {
      record = {};
    }

    const notes = (input.outcomeNotes ?? "").trim() || null;
    let paperTag = (input.paperTag ?? "").trim() || null;
    if (paperTag && paperTag.length > 120) {
      paperTag = paperTag.slice(0, 120);
    }
    const horizonRef = reviewHorizonRefFromFrozen(record);
    const now = utcIsoNow();
    const sid = String(input.snapshotId);

    const existing = db
      .prepare("SELECT id FROM snapshot_reviews WHERE snapshot_id = ?")
      .get(sid) as { id: string } | undefined;

    if (existing) {
      db.prepare(
        `UPDATE snapshot_reviews
         SET review_status = ?, outcome_notes = ?, reviewed_at_utc = ?,
             review_horizon_ref = ?, paper_tag = ?
         WHERE snapshot_id = ?`,
      ).run(status, notes, now, horizonRef, paperTag, sid);
    } else {
      db.prepare(
        `INSERT INTO snapshot_reviews
         (id, snapshot_id, review_status, outcome_notes, reviewed_at_utc,
          review_horizon_ref, paper_tag)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
      ).run(randomUUID(), sid, status, notes, now, horizonRef, paperTag);
    }

    const saved = db
      .prepare(
        `SELECT id, snapshot_id, review_status, outcome_notes, reviewed_at_utc,
                review_horizon_ref, paper_tag
         FROM snapshot_reviews WHERE snapshot_id = ?`,
      )
      .get(sid) as {
      id: string;
      snapshot_id: string;
      review_status: string;
      outcome_notes: string | null;
      reviewed_at_utc: string;
      review_horizon_ref: string | null;
      paper_tag: string | null;
    };

    return { ok: true, review: mapReviewRow(saved) };
  } catch (err) {
    const message = err instanceof Error ? err.message : "review save failed";
    return { ok: false, error: message, httpStatus: 500 };
  } finally {
    db?.close();
  }
}
