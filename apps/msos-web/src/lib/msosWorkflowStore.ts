import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
import { randomUUID } from "crypto";

import type { ExpressionRecord } from "@/lib/expressionPersistence";
import type { ThesisRecord } from "@/lib/thesisPersistence";
import { normalizeOwnerEmail } from "@/lib/msosIdentity";

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

type OwnerPointers = {
  thesisId: string | null;
  expressionId: string | null;
};

type WorkflowStoreFile = {
  version: 1 | 2;
  theses: StoredThesis[];
  expressions: StoredExpression[];
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
  const normalized = normalizeOwnerEmail(ownerEmail);
  return normalized ?? "__anon__";
}

function normalizeStore(raw: Partial<WorkflowStoreFile>): WorkflowStoreFile {
  const theses = Array.isArray(raw.theses) ? (raw.theses as StoredThesis[]) : [];
  const expressions = Array.isArray(raw.expressions) ? (raw.expressions as StoredExpression[]) : [];
  const currentByOwner: Record<string, OwnerPointers> = { ...(raw.currentByOwner ?? {}) };
  if (raw.version !== 2) {
    currentByOwner.__anon__ = {
      thesisId: typeof raw.currentThesisId === "string" ? raw.currentThesisId : null,
      expressionId: typeof raw.currentExpressionId === "string" ? raw.currentExpressionId : null,
    };
  }
  return {
    version: 2,
    theses,
    expressions,
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

function thesisOwnerMatches(row: StoredThesis, ownerEmail: string): boolean {
  const key = ownerKey(ownerEmail);
  const rowOwner = normalizeOwnerEmail(row.ownerEmail ?? null);
  if (key === "__anon__") {
    return rowOwner === null;
  }
  return rowOwner === key;
}

function expressionOwnerMatches(row: StoredExpression, ownerEmail: string): boolean {
  const key = ownerKey(ownerEmail);
  const rowOwner = normalizeOwnerEmail(row.ownerEmail ?? null);
  if (key === "__anon__") {
    return rowOwner === null;
  }
  return rowOwner === key;
}

function pointersForOwner(store: WorkflowStoreFile, ownerEmail: string): OwnerPointers {
  const key = ownerKey(ownerEmail);
  return store.currentByOwner?.[key] ?? { thesisId: null, expressionId: null };
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
  const owner = normalizeOwnerEmail(ownerEmail);
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
  const existing = pointers.expressionId
    ? store.expressions.find(
        (row) => row.id === pointers.expressionId && expressionOwnerMatches(row, ownerEmail),
      )
    : undefined;
  const owner = normalizeOwnerEmail(ownerEmail);
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
  });
  await writeStore({
    ...nextStore,
    expressions,
  });
  return next;
}

export async function loadWorkflowSummary(ownerEmail: string): Promise<WorkflowSummary> {
  const store = await readStore();
  const scopedTheses = store.theses.filter((row) => thesisOwnerMatches(row, ownerEmail));
  const scopedExpressions = store.expressions.filter((row) => expressionOwnerMatches(row, ownerEmail));
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

  const owner = normalizeOwnerEmail(ownerEmail);
  const sourceLabel = owner
    ? `Your workspace · ${owner}`
    : "Your workspace";

  return {
    sourceLabel,
    kpis,
    currentWork,
  };
}
