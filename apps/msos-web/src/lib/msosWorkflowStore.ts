import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
import { randomUUID } from "crypto";

import type { ExpressionRecord, PaperTradeStatus } from "@/lib/expressionPersistence";
import type { HorizonRegionIntent } from "@/lib/horizonRegion";
import type { ThesisRecord } from "@/lib/thesisPersistence";
import { normalizeOwnerEmail } from "@/lib/msosIdentityCore";
import { scopeOwnerId } from "@/lib/msosSession";

export const MSOS_WORKFLOW_STORE_FILENAME = "msos_workflow_v1.json";

export type StoredThesis = ThesisRecord & {
  id: string;
  ownerEmail?: string | null;
  linkedSnapshotId?: string | null;
};

export type StoredExpression = ExpressionRecord & {
  id: string;
  thesisId: string;
  ownerEmail?: string | null;
};

export type StoredHorizonRegion = HorizonRegionIntent & {
  kind: "horizon_region";
  ownerEmail?: string | null;
};

type OwnerPointers = {
  thesisId: string | null;
  expressionId: string | null;
  horizonRegionId: string | null;
};

type WorkflowStoreFile = {
  version: 1 | 2;
  theses: StoredThesis[];
  expressions: StoredExpression[];
  horizonRegions?: StoredHorizonRegion[];
  currentThesisId: string | null;
  currentExpressionId: string | null;
  currentByOwner?: Record<string, OwnerPointers>;
};

export type WorkflowSummaryKpi = {
  label: string;
  value: string;
  sub: string;
  tone?: string;
};

export type WorkflowSummaryWorkItem = {
  name: string;
  tag: string;
  detail: string;
  tagTone?: string;
};

export type WorkflowSummary = {
  sourceLabel: string;
  kpis: WorkflowSummaryKpi[];
  currentWork: WorkflowSummaryWorkItem[];
};

const EMPTY_STORE: WorkflowStoreFile = {
  version: 2,
  theses: [],
  expressions: [],
  horizonRegions: [],
  currentThesisId: null,
  currentExpressionId: null,
  currentByOwner: {},
};

export function workflowStoreDir(): string {
  const raw = process.env.MSOS_WORKFLOW_STORE_DIR?.trim() || process.env.PPE_WEB_FEEDBACK_DIR?.trim();
  if (raw) return raw;
  return path.join(process.cwd(), "data");
}

export function workflowStorePath(): string {
  const explicit = process.env.MSOS_WORKFLOW_STORE_PATH?.trim();
  if (explicit) return explicit;
  return path.join(workflowStoreDir(), MSOS_WORKFLOW_STORE_FILENAME);
}

function ownerKey(ownerEmail: string): string {
  const scoped = scopeOwnerId(ownerEmail);
  if (scoped?.startsWith("session:")) return scoped;
  const normalized = normalizeOwnerEmail(ownerEmail);
  return normalized ?? "__anon__";
}

function storedOwnerKey(raw: string | null | undefined): string {
  const scoped = scopeOwnerId(raw);
  if (scoped?.startsWith("session:")) return scoped;
  const normalized = normalizeOwnerEmail(raw);
  return normalized ?? "__anon__";
}

function normalizeOwnerPointers(raw: Partial<OwnerPointers> | undefined): OwnerPointers {
  return {
    thesisId: typeof raw?.thesisId === "string" ? raw.thesisId : null,
    expressionId: typeof raw?.expressionId === "string" ? raw.expressionId : null,
    horizonRegionId: typeof raw?.horizonRegionId === "string" ? raw.horizonRegionId : null,
  };
}

function normalizeStore(raw: Partial<WorkflowStoreFile>): WorkflowStoreFile {
  const theses = Array.isArray(raw.theses) ? (raw.theses as StoredThesis[]) : [];
  const expressions = Array.isArray(raw.expressions) ? (raw.expressions as StoredExpression[]) : [];
  const horizonRegions = Array.isArray(raw.horizonRegions)
    ? (raw.horizonRegions as StoredHorizonRegion[])
    : [];
  const currentByOwner: Record<string, OwnerPointers> = {};
  for (const [key, pointers] of Object.entries(raw.currentByOwner ?? {})) {
    currentByOwner[key] = normalizeOwnerPointers(pointers);
  }
  if (raw.version !== 2) {
    currentByOwner.__anon__ = {
      thesisId: typeof raw.currentThesisId === "string" ? raw.currentThesisId : null,
      expressionId: typeof raw.currentExpressionId === "string" ? raw.currentExpressionId : null,
      horizonRegionId: null,
    };
  }
  return {
    version: 2,
    theses,
    expressions,
    horizonRegions,
    currentThesisId: typeof raw.currentThesisId === "string" ? raw.currentThesisId : null,
    currentExpressionId: typeof raw.currentExpressionId === "string" ? raw.currentExpressionId : null,
    currentByOwner,
  };
}

async function readStore(): Promise<WorkflowStoreFile> {
  const filePath = workflowStorePath();
  try {
    const raw = await readFile(filePath, "utf8");
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return { ...EMPTY_STORE };
    }
    return normalizeStore(parsed as Partial<WorkflowStoreFile>);
  } catch {
    return { ...EMPTY_STORE };
  }
}

async function writeStore(store: WorkflowStoreFile): Promise<void> {
  const filePath = workflowStorePath();
  await mkdir(path.dirname(filePath), { recursive: true });
  const payload: WorkflowStoreFile = {
    ...store,
    version: 2,
    currentByOwner: store.currentByOwner ?? {},
  };
  await writeFile(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function isThesisRecord(value: unknown): value is ThesisRecord {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  return (
    typeof row.instrument === "string" &&
    typeof row.horizonDays === "number" &&
    typeof row.marketRangePct === "number" &&
    typeof row.thesisRangePct === "number" &&
    typeof row.referenceLabel === "string" &&
    typeof row.trustLabel === "string" &&
    (row.lifecycle === "exploring" || row.lifecycle === "draft" || row.lifecycle === "confirmed") &&
    typeof row.updatedAt === "string"
  );
}

function isExpressionRecord(value: unknown): value is ExpressionRecord {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  return (
    typeof row.familyId === "string" &&
    typeof row.planHeadline === "string" &&
    typeof row.planSummary === "string" &&
    Array.isArray(row.legs) &&
    (row.lifecycle === "planned" || row.lifecycle === "simulated") &&
    typeof row.updatedAt === "string"
  );
}

function isHorizonRegionIntent(value: unknown): value is HorizonRegionIntent {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  const region = row.region;
  if (!region || typeof region !== "object") return false;
  const box = region as Record<string, unknown>;
  return (
    row.schema_version === 1 &&
    typeof row.id === "string" &&
    typeof row.asset_id === "string" &&
    typeof row.venue === "string" &&
    typeof row.created_at_utc === "string" &&
    typeof box.time_start_utc === "string" &&
    typeof box.time_end_utc === "string" &&
    typeof box.price_min_usd === "number" &&
    typeof box.price_max_usd === "number" &&
    (row.bias === "bullish_in_region" ||
      row.bias === "bearish_in_region" ||
      row.bias === "neutral")
  );
}

function thesisOwnerMatches(row: StoredThesis, ownerEmail: string): boolean {
  return storedOwnerKey(row.ownerEmail) === ownerKey(ownerEmail);
}

function expressionOwnerMatches(row: StoredExpression, ownerEmail: string): boolean {
  return storedOwnerKey(row.ownerEmail) === ownerKey(ownerEmail);
}

function pointersForOwner(store: WorkflowStoreFile, ownerEmail: string): OwnerPointers {
  const key = ownerKey(ownerEmail);
  return normalizeOwnerPointers(store.currentByOwner?.[key]);
}

function horizonRegionOwnerMatches(row: StoredHorizonRegion, ownerEmail: string): boolean {
  return storedOwnerKey(row.ownerEmail) === ownerKey(ownerEmail);
}

function persistPointers(
  store: WorkflowStoreFile,
  ownerEmail: string,
  pointers: OwnerPointers,
): WorkflowStoreFile {
  const key = ownerKey(ownerEmail);
  return {
    ...store,
    currentByOwner: {
      ...(store.currentByOwner ?? {}),
      [key]: pointers,
    },
  };
}

export async function getCurrentThesis(ownerEmail: string): Promise<StoredThesis | null> {
  const store = await readStore();
  const pointers = pointersForOwner(store, ownerEmail);
  if (!pointers.thesisId) return null;
  return (
    store.theses.find(
      (row) => row.id === pointers.thesisId && thesisOwnerMatches(row, ownerEmail),
    ) ?? null
  );
}

export async function getCurrentExpression(ownerEmail: string): Promise<StoredExpression | null> {
  const store = await readStore();
  const pointers = pointersForOwner(store, ownerEmail);
  if (!pointers.expressionId) return null;
  return (
    store.expressions.find(
      (row) => row.id === pointers.expressionId && expressionOwnerMatches(row, ownerEmail),
    ) ?? null
  );
}

export async function upsertCurrentThesis(
  thesis: ThesisRecord,
  ownerEmail: string,
  linkedSnapshotId?: string | null,
): Promise<StoredThesis> {
  if (!isThesisRecord(thesis)) {
    throw new Error("invalid thesis record");
  }
  const store = await readStore();
  const pointers = pointersForOwner(store, ownerEmail);
  const existing = pointers.thesisId
    ? store.theses.find(
        (row) => row.id === pointers.thesisId && thesisOwnerMatches(row, ownerEmail),
      )
    : undefined;
  const owner = scopeOwnerId(ownerEmail) ?? normalizeOwnerEmail(ownerEmail);
  const next: StoredThesis = {
    ...thesis,
    id: existing?.id ?? randomUUID(),
    ownerEmail: owner,
    linkedSnapshotId: linkedSnapshotId ?? existing?.linkedSnapshotId ?? null,
  };
  const theses = store.theses.filter((row) => row.id !== next.id);
  theses.push(next);
  const nextStore = persistPointers(store, ownerEmail, {
    thesisId: next.id,
    expressionId: pointers.expressionId,
    horizonRegionId: pointers.horizonRegionId,
  });
  await writeStore({
    ...nextStore,
    theses,
  });
  return next;
}

export async function upsertCurrentExpression(
  expression: ExpressionRecord,
  ownerEmail: string,
): Promise<StoredExpression> {
  if (!isExpressionRecord(expression)) {
    throw new Error("invalid expression record");
  }
  const store = await readStore();
  const pointers = pointersForOwner(store, ownerEmail);
  const thesisId = pointers.thesisId;
  if (!thesisId) {
    throw new Error("confirm a thesis before saving expression");
  }
  const existing =
    expression.lifecycle === "planned" && pointers.expressionId
      ? store.expressions.find(
          (row) =>
            row.id === pointers.expressionId &&
            expressionOwnerMatches(row, ownerEmail) &&
            row.lifecycle === "planned",
        )
      : undefined;
  const owner = scopeOwnerId(ownerEmail) ?? normalizeOwnerEmail(ownerEmail);
  const next: StoredExpression = {
    ...expression,
    id: existing?.id ?? randomUUID(),
    thesisId,
    ownerEmail: owner,
  };
  const expressions = store.expressions.filter((row) => row.id !== next.id);
  expressions.push(next);
  const nextStore = persistPointers(store, ownerEmail, {
    thesisId: pointers.thesisId,
    expressionId: next.id,
    horizonRegionId: pointers.horizonRegionId,
  });
  await writeStore({
    ...nextStore,
    expressions,
  });
  return next;
}

export async function appendPaperTrade(
  expression: ExpressionRecord,
  ownerEmail: string,
): Promise<StoredExpression> {
  if (!isExpressionRecord(expression)) {
    throw new Error("invalid expression record");
  }
  if (expression.lifecycle !== "simulated") {
    throw new Error("paper trades must use simulated lifecycle");
  }
  const store = await readStore();
  const pointers = pointersForOwner(store, ownerEmail);
  const thesisId = pointers.thesisId;
  if (!thesisId) {
    throw new Error("confirm a thesis before saving a paper trade");
  }
  const owner = scopeOwnerId(ownerEmail) ?? normalizeOwnerEmail(ownerEmail);
  const savedAt = expression.savedAt ?? expression.updatedAt ?? new Date().toISOString();
  const next: StoredExpression = {
    ...expression,
    lifecycle: "simulated",
    paperTradeStatus: expression.paperTradeStatus ?? "open",
    savedAt,
    updatedAt: savedAt,
    id: randomUUID(),
    thesisId,
    ownerEmail: owner,
  };
  const expressions = [...store.expressions, next];
  const nextStore = persistPointers(store, ownerEmail, {
    thesisId: pointers.thesisId,
    expressionId: next.id,
    horizonRegionId: pointers.horizonRegionId,
  });
  await writeStore({
    ...nextStore,
    expressions,
  });
  return next;
}

export function effectivePaperTradeStatus(trade: StoredExpression): PaperTradeStatus {
  const stored = trade.paperTradeStatus ?? "open";
  if (stored === "closed") {
    return "closed";
  }
  const exp = trade.expiryDate?.trim();
  if (exp) {
    const iso = exp.length <= 10 ? `${exp}T23:59:59.999Z` : exp;
    const end = Date.parse(iso);
    if (!Number.isNaN(end) && end < Date.now()) {
      return "expired";
    }
  }
  return stored === "expired" ? "expired" : "open";
}

function withEffectiveStatus(trade: StoredExpression): StoredExpression {
  const status = effectivePaperTradeStatus(trade);
  if (status === trade.paperTradeStatus) {
    return trade;
  }
  return { ...trade, paperTradeStatus: status };
}

export async function listPaperTrades(ownerEmail: string): Promise<StoredExpression[]> {
  const store = await readStore();
  return store.expressions
    .filter((row) => expressionOwnerMatches(row, ownerEmail) && row.lifecycle === "simulated")
    .map(withEffectiveStatus)
    .sort((a, b) => {
      const aTs = Date.parse(a.savedAt ?? a.updatedAt);
      const bTs = Date.parse(b.savedAt ?? b.updatedAt);
      return (Number.isNaN(bTs) ? 0 : bTs) - (Number.isNaN(aTs) ? 0 : aTs);
    });
}

export async function listOpenPaperTrades(ownerEmail: string): Promise<StoredExpression[]> {
  const trades = await listPaperTrades(ownerEmail);
  return trades.filter((row) => effectivePaperTradeStatus(row) === "open");
}

export async function getPaperTradeById(
  ownerEmail: string,
  tradeId: string,
): Promise<StoredExpression | null> {
  const store = await readStore();
  const row = store.expressions.find(
    (expression) =>
      expression.id === tradeId &&
      expression.lifecycle === "simulated" &&
      expressionOwnerMatches(expression, ownerEmail),
  );
  return row ? withEffectiveStatus(row) : null;
}

export async function deletePaperTrade(ownerEmail: string, tradeId: string): Promise<boolean> {
  const store = await readStore();
  const target = store.expressions.find(
    (row) =>
      row.id === tradeId &&
      row.lifecycle === "simulated" &&
      expressionOwnerMatches(row, ownerEmail),
  );
  if (!target) {
    return false;
  }
  const expressions = store.expressions.filter((row) => row.id !== tradeId);
  const pointers = pointersForOwner(store, ownerEmail);
  const expressionId = pointers.expressionId === tradeId ? null : pointers.expressionId;
  const nextStore = persistPointers(store, ownerEmail, {
    thesisId: pointers.thesisId,
    expressionId,
    horizonRegionId: pointers.horizonRegionId,
  });
  await writeStore({ ...nextStore, expressions });
  return true;
}

export async function restorePaperTrade(
  ownerEmail: string,
  trade: StoredExpression,
): Promise<StoredExpression | null> {
  if (trade.lifecycle !== "simulated") {
    return null;
  }
  if (!expressionOwnerMatches(trade, ownerEmail)) {
    return null;
  }
  const store = await readStore();
  const existing = store.expressions.find(
    (row) => row.id === trade.id && expressionOwnerMatches(row, ownerEmail),
  );
  if (existing) {
    return withEffectiveStatus(existing);
  }
  const owner = scopeOwnerId(ownerEmail) ?? normalizeOwnerEmail(ownerEmail);
  const restored: StoredExpression = {
    ...trade,
    ownerEmail: owner,
    lifecycle: "simulated",
  };
  const expressions = [...store.expressions, restored];
  const pointers = pointersForOwner(store, ownerEmail);
  const nextStore = persistPointers(store, ownerEmail, {
    thesisId: pointers.thesisId ?? trade.thesisId,
    expressionId: pointers.expressionId ?? trade.id,
    horizonRegionId: pointers.horizonRegionId,
  });
  await writeStore({ ...nextStore, expressions });
  return withEffectiveStatus(restored);
}

export async function clearPaperTrades(ownerEmail: string): Promise<number> {
  const store = await readStore();
  const toRemove = new Set(
    store.expressions
      .filter(
        (row) => row.lifecycle === "simulated" && expressionOwnerMatches(row, ownerEmail),
      )
      .map((row) => row.id),
  );
  if (toRemove.size === 0) {
    return 0;
  }
  const expressions = store.expressions.filter((row) => !toRemove.has(row.id));
  const pointers = pointersForOwner(store, ownerEmail);
  const expressionId =
    pointers.expressionId && toRemove.has(pointers.expressionId) ? null : pointers.expressionId;
  const nextStore = persistPointers(store, ownerEmail, {
    thesisId: pointers.thesisId,
    expressionId,
    horizonRegionId: pointers.horizonRegionId,
  });
  await writeStore({ ...nextStore, expressions });
  return toRemove.size;
}

export async function closePaperTrade(
  ownerEmail: string,
  tradeId: string,
): Promise<StoredExpression | null> {
  const store = await readStore();
  const idx = store.expressions.findIndex(
    (row) =>
      row.id === tradeId &&
      row.lifecycle === "simulated" &&
      expressionOwnerMatches(row, ownerEmail),
  );
  if (idx < 0) {
    return null;
  }
  const current = store.expressions[idx];
  if (effectivePaperTradeStatus(current) !== "open") {
    return withEffectiveStatus(current);
  }
  const closedAt = new Date().toISOString();
  const next: StoredExpression = {
    ...current,
    paperTradeStatus: "closed",
    closedAt,
    updatedAt: closedAt,
  };
  const expressions = [...store.expressions];
  expressions[idx] = next;
  await writeStore({ ...store, expressions });
  return next;
}

export async function getHorizonRegionById(
  ownerEmail: string,
  regionId: string,
): Promise<StoredHorizonRegion | null> {
  const store = await readStore();
  return (
    store.horizonRegions?.find(
      (row) => row.id === regionId && horizonRegionOwnerMatches(row, ownerEmail),
    ) ?? null
  );
}

export async function getCurrentHorizonRegion(ownerEmail: string): Promise<StoredHorizonRegion | null> {
  const store = await readStore();
  const pointers = pointersForOwner(store, ownerEmail);
  if (!pointers.horizonRegionId) return null;
  return (
    store.horizonRegions?.find(
      (row) => row.id === pointers.horizonRegionId && horizonRegionOwnerMatches(row, ownerEmail),
    ) ?? null
  );
}

export async function upsertHorizonRegion(
  region: HorizonRegionIntent,
  ownerEmail: string,
): Promise<StoredHorizonRegion> {
  if (!isHorizonRegionIntent(region)) {
    throw new Error("invalid horizon region");
  }
  const store = await readStore();
  const pointers = pointersForOwner(store, ownerEmail);
  const existing =
    store.horizonRegions?.find(
      (row) => row.id === region.id && horizonRegionOwnerMatches(row, ownerEmail),
    ) ??
    (pointers.horizonRegionId
      ? store.horizonRegions?.find(
          (row) =>
            row.id === pointers.horizonRegionId && horizonRegionOwnerMatches(row, ownerEmail),
        )
      : undefined);
  const owner = scopeOwnerId(ownerEmail) ?? normalizeOwnerEmail(ownerEmail);
  const next: StoredHorizonRegion = {
    ...region,
    id: existing?.id ?? region.id,
    kind: "horizon_region",
    ownerEmail: owner,
  };
  const horizonRegions = (store.horizonRegions ?? []).filter((row) => row.id !== next.id);
  horizonRegions.push(next);
  const nextStore = persistPointers(store, ownerEmail, {
    thesisId: pointers.thesisId,
    expressionId: pointers.expressionId,
    horizonRegionId: next.id,
  });
  await writeStore({
    ...nextStore,
    horizonRegions,
  });
  return next;
}

export async function loadWorkflowSummary(ownerEmail: string): Promise<WorkflowSummary> {
  const store = await readStore();
  const scopedTheses = store.theses.filter((row) => thesisOwnerMatches(row, ownerEmail));
  const scopedExpressions = store.expressions.filter((row) => expressionOwnerMatches(row, ownerEmail));
  const paperTrades = scopedExpressions.filter((row) => row.lifecycle === "simulated");
  const pointers = pointersForOwner(store, ownerEmail);
  const draftCount = scopedTheses.filter((row) => row.lifecycle === "draft").length;
  const confirmedCount = scopedTheses.filter((row) => row.lifecycle === "confirmed").length;
  const currentThesis = pointers.thesisId
    ? scopedTheses.find((row) => row.id === pointers.thesisId)
    : undefined;
  const currentExpression = pointers.expressionId
    ? scopedExpressions.find((row) => row.id === pointers.expressionId)
    : undefined;

  const kpis: WorkflowSummaryKpi[] = [
    {
      label: "Draft views",
      value: String(draftCount),
      sub: "Your workspace",
      tone: draftCount > 0 ? "amber" : undefined,
    },
    {
      label: "Confirmed views",
      value: String(confirmedCount),
      sub: "Your workspace",
      tone: confirmedCount > 0 ? "teal" : undefined,
    },
    {
      label: "Paper trades",
      value: String(paperTrades.length),
      sub: "Saved plans",
      tone: paperTrades.length > 0 ? "teal" : undefined,
    },
  ];

  const currentWork: WorkflowSummaryWorkItem[] = [];
  if (currentThesis) {
    currentWork.push({
      name: currentThesis.instrument,
      tag: currentThesis.lifecycle === "confirmed" ? "Confirmed" : "Draft",
      detail: `${currentThesis.horizonDays}d horizon · ${currentThesis.referenceLabel}`,
      tagTone: currentThesis.lifecycle === "confirmed" ? "teal" : "amber",
    });
  }
  if (currentExpression) {
    currentWork.push({
      name: currentExpression.planHeadline,
      tag: currentExpression.lifecycle === "simulated" ? "Simulated" : "Planned",
      detail: currentExpression.planSummary,
      tagTone: currentExpression.lifecycle === "simulated" ? "teal" : undefined,
    });
  }

  const owner = scopeOwnerId(ownerEmail) ?? normalizeOwnerEmail(ownerEmail);
  const sourceLabel = owner
    ? `Your workspace · ${owner}`
    : "Your workspace";

  return {
    sourceLabel,
    kpis,
    currentWork,
  };
}
