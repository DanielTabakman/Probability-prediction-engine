import { appendFileSync, mkdirSync } from "fs";
import path from "path";

import Database from "better-sqlite3";

import { normalizeOwnerEmail } from "@/lib/msosIdentity";
import { workflowStoreDir } from "@/lib/msosWorkflowStore";

export type EntitlementTier = "free" | "research_beta" | "paid";

export type SubscriptionStatus = "none" | "active" | "past_due" | "canceled";

export type MsosEntitlement = {
  ownerEmail: string;
  tier: EntitlementTier;
  grantedAtUtc: string;
  grantedBy: string;
  notes: string | null;
  stripeCustomerId: string | null;
  stripeSubscriptionId: string | null;
  subscriptionStatus: SubscriptionStatus;
};

export type EntitlementGateResult =
  | { ok: true; entitlement: MsosEntitlement }
  | { ok: false; requiredTier: EntitlementTier; currentTier: EntitlementTier };

const TIER_RANK: Record<EntitlementTier, number> = {
  free: 0,
  research_beta: 1,
  paid: 2,
};

const TIER_LABELS: Record<EntitlementTier, string> = {
  free: "Free",
  research_beta: "Research beta",
  paid: "Paid",
};

export function entitlementsDbPath(): string {
  const explicit = process.env.MSOS_ENTITLEMENTS_DB_PATH?.trim();
  if (explicit) return explicit;
  return path.join(workflowStoreDir(), "msos_entitlements.sqlite3");
}

export function upgradeOfferUrl(): string | null {
  const raw = process.env.MSOS_UPGRADE_OFFER_URL?.trim();
  return raw || null;
}

export function tierLabel(tier: EntitlementTier): string {
  return TIER_LABELS[tier];
}

function utcNow(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function ensureDb(): Database.Database {
  const dbPath = entitlementsDbPath();
  mkdirSync(path.dirname(dbPath), { recursive: true });
  const db = new Database(dbPath);
  db.exec(`
    CREATE TABLE IF NOT EXISTS msos_entitlements (
      owner_email TEXT PRIMARY KEY NOT NULL,
      tier TEXT NOT NULL,
      granted_at_utc TEXT NOT NULL,
      granted_by TEXT NOT NULL,
      notes TEXT,
      stripe_customer_id TEXT,
      stripe_subscription_id TEXT,
      subscription_status TEXT NOT NULL DEFAULT 'none'
    );
  `);
  return db;
}

function rowToEntitlement(row: Record<string, unknown>): MsosEntitlement {
  return {
    ownerEmail: String(row.owner_email),
    tier: String(row.tier) as EntitlementTier,
    grantedAtUtc: String(row.granted_at_utc),
    grantedBy: String(row.granted_by),
    notes: row.notes == null ? null : String(row.notes),
    stripeCustomerId: row.stripe_customer_id == null ? null : String(row.stripe_customer_id),
    stripeSubscriptionId:
      row.stripe_subscription_id == null ? null : String(row.stripe_subscription_id),
    subscriptionStatus: String(row.subscription_status || "none") as SubscriptionStatus,
  };
}

export function getEntitlement(ownerEmail: string): MsosEntitlement | null {
  const email = normalizeOwnerEmail(ownerEmail);
  if (!email) return null;
  const db = ensureDb();
  try {
    const row = db
      .prepare(
        `SELECT owner_email, tier, granted_at_utc, granted_by, notes,
                stripe_customer_id, stripe_subscription_id, subscription_status
         FROM msos_entitlements WHERE owner_email = ?`,
      )
      .get(email) as Record<string, unknown> | undefined;
    return row ? rowToEntitlement(row) : null;
  } finally {
    db.close();
  }
}

export function getOrCreateEntitlement(ownerEmail: string): MsosEntitlement | null {
  const email = normalizeOwnerEmail(ownerEmail);
  if (!email) return null;
  const existing = getEntitlement(email);
  if (existing) return existing;

  const db = ensureDb();
  try {
    const now = utcNow();
    db.prepare(
      `INSERT INTO msos_entitlements
       (owner_email, tier, granted_at_utc, granted_by, notes, subscription_status)
       VALUES (?, 'free', ?, 'system', 'default free tier on first visit', 'none')`,
    ).run(email, now);
    return getEntitlement(email);
  } finally {
    db.close();
  }
}

export function tierMeetsRequirement(
  current: EntitlementTier,
  required: EntitlementTier,
): boolean {
  return TIER_RANK[current] >= TIER_RANK[required];
}

export function checkEntitlementGate(
  ownerEmail: string,
  requiredTier: EntitlementTier = "free",
): EntitlementGateResult {
  const entitlement = getOrCreateEntitlement(ownerEmail);
  if (!entitlement) {
    return { ok: false, requiredTier, currentTier: "free" };
  }
  if (!tierMeetsRequirement(entitlement.tier, requiredTier)) {
    return { ok: false, requiredTier, currentTier: entitlement.tier };
  }
  return { ok: true, entitlement };
}

export function upgradeRequestsLogPath(): string {
  const raw = process.env.MSOS_UPGRADE_REQUESTS_LOG?.trim();
  if (raw) return raw;
  return path.join(workflowStoreDir(), "msos_upgrade_requests.jsonl");
}

export function appendUpgradeRequest(ownerEmail: string, note = ""): void {
  const email = normalizeOwnerEmail(ownerEmail);
  if (!email) return;
  const logPath = upgradeRequestsLogPath();
  mkdirSync(path.dirname(logPath), { recursive: true });
  const entry = {
    ownerEmail: email,
    requestedAtUtc: utcNow(),
    note: note.trim() || null,
    upgradeUrl: upgradeOfferUrl(),
  };
  appendFileSync(logPath, `${JSON.stringify(entry)}\n`, "utf8");
}
