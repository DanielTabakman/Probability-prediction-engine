import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
import { randomUUID } from "crypto";

import type { ExpressionRecord } from "@/lib/expressionPersistence";
import type { ThesisRecord } from "@/lib/thesisPersistence";

export const MSOS_WORKFLOW_STORE_FILENAME = "msos_workflow_v1.json";

export type StoredThesis = ThesisRecord & {
  id: string;
  linkedSnapshotId?: string | null;
};

export type StoredExpression = ExpressionRecord & {
  id: string;
  thesisId: string;
};

type WorkflowStoreFile = {
  version: 1;
  theses: StoredThesis[];
  expressions: StoredExpression[];
  currentThesisId: string | null;
  currentExpressionId: string | null;
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
  version: 1,
  theses: [],
  expressions: [],
  currentThesisId: null,
  currentExpressionId: null,
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

async function readStore(): Promise<WorkflowStoreFile> {
  const filePath = workflowStorePath();
  try {
    const raw = await readFile(filePath, "utf8");
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return { ...EMPTY_STORE };
    }
    const row = parsed as Partial<WorkflowStoreFile>;
    return {
      version: 1,
      theses: Array.isArray(row.theses) ? (row.theses as StoredThesis[]) : [],
      expressions: Array.isArray(row.expressions) ? (row.expressions as StoredExpression[]) : [],
      currentThesisId: typeof row.currentThesisId === "string" ? row.currentThesisId : null,
      currentExpressionId: typeof row.currentExpressionId === "string" ? row.currentExpressionId : null,
    };
  } catch {
    return { ...EMPTY_STORE };
  }
}

async function writeStore(store: WorkflowStoreFile): Promise<void> {
  const filePath = workflowStorePath();
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, `${JSON.stringify(store, null, 2)}\n`, "utf8");
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

export async function getCurrentThesis(): Promise<StoredThesis | null> {
  const store = await readStore();
  if (!store.currentThesisId) return null;
  return store.theses.find((row) => row.id === store.currentThesisId) ?? null;
}

export async function getCurrentExpression(): Promise<StoredExpression | null> {
  const store = await readStore();
  if (!store.currentExpressionId) return null;
  return store.expressions.find((row) => row.id === store.currentExpressionId) ?? null;
}

export async function upsertCurrentThesis(
  thesis: ThesisRecord,
  linkedSnapshotId?: string | null,
): Promise<StoredThesis> {
  if (!isThesisRecord(thesis)) {
    throw new Error("invalid thesis record");
  }
  const store = await readStore();
  const existing = store.currentThesisId
    ? store.theses.find((row) => row.id === store.currentThesisId)
    : undefined;
  const next: StoredThesis = {
    ...thesis,
    id: existing?.id ?? randomUUID(),
    linkedSnapshotId: linkedSnapshotId ?? existing?.linkedSnapshotId ?? null,
  };
  const theses = store.theses.filter((row) => row.id !== next.id);
  theses.push(next);
  await writeStore({
    ...store,
    theses,
    currentThesisId: next.id,
  });
  return next;
}

export async function upsertCurrentExpression(expression: ExpressionRecord): Promise<StoredExpression> {
  if (!isExpressionRecord(expression)) {
    throw new Error("invalid expression record");
  }
  const store = await readStore();
  const thesisId = store.currentThesisId;
  if (!thesisId) {
    throw new Error("confirm a thesis before saving expression");
  }
  const existing = store.currentExpressionId
    ? store.expressions.find((row) => row.id === store.currentExpressionId)
    : undefined;
  const next: StoredExpression = {
    ...expression,
    id: existing?.id ?? randomUUID(),
    thesisId,
  };
  const expressions = store.expressions.filter((row) => row.id !== next.id);
  expressions.push(next);
  await writeStore({
    ...store,
    expressions,
    currentExpressionId: next.id,
  });
  return next;
}

export async function loadWorkflowSummary(): Promise<WorkflowSummary> {
  const store = await readStore();
  const draftCount = store.theses.filter((row) => row.lifecycle === "draft").length;
  const confirmedCount = store.theses.filter((row) => row.lifecycle === "confirmed").length;
  const currentThesis = store.currentThesisId
    ? store.theses.find((row) => row.id === store.currentThesisId)
    : undefined;
  const currentExpression = store.currentExpressionId
    ? store.expressions.find((row) => row.id === store.currentExpressionId)
    : undefined;

  const kpis: WorkflowSummaryKpi[] = [
    {
      label: "Draft thesis",
      value: String(draftCount),
      sub: "MSOS workflow store",
      tone: draftCount > 0 ? "amber" : undefined,
    },
    {
      label: "Confirmed thesis",
      value: String(confirmedCount),
      sub: "MSOS workflow store",
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

  return {
    sourceLabel: "From MSOS workflow store",
    kpis,
    currentWork,
  };
}
