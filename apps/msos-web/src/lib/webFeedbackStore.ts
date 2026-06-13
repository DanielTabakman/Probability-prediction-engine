import { randomUUID } from "crypto";
import fs from "fs";
import path from "path";

import {
  TRADER_PROFILES,
  type TraderProfile,
  type UnderstoodAnswer,
  type WebFeedbackEntry,
  type WebFeedbackSubmitPayload,
  type WouldReturnAnswer,
} from "@/lib/webFeedbackTypes";

const UNDERSTOOD: UnderstoodAnswer[] = ["yes", "not_yet"];
const WOULD_RETURN: WouldReturnAnswer[] = ["yes", "no"];
const MAX_NOTE_LEN = 300;

function feedbackDir(): string {
  const raw = (process.env.PPE_WEB_FEEDBACK_DIR ?? "").trim();
  if (raw) {
    return path.resolve(raw);
  }
  return path.resolve(process.cwd(), "..", "..", "data");
}

export function feedbackFilePath(): string {
  return path.join(feedbackDir(), "ppe_web_feedback.jsonl");
}

function ensureDir(): void {
  fs.mkdirSync(feedbackDir(), { recursive: true });
}

function utcIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function isTraderProfile(value: string): value is TraderProfile {
  return (TRADER_PROFILES as readonly string[]).includes(value);
}

export function validateSubmitPayload(body: unknown): WebFeedbackSubmitPayload {
  if (!body || typeof body !== "object") {
    throw new Error("invalid body");
  }
  const raw = body as Record<string, unknown>;
  const understood = String(raw.understood ?? "").trim() as UnderstoodAnswer;
  const would_return = String(raw.would_return ?? "").trim() as WouldReturnAnswer;
  const trader_profile = String(raw.trader_profile ?? "").trim();
  if (!UNDERSTOOD.includes(understood)) {
    throw new Error("invalid understood");
  }
  if (!WOULD_RETURN.includes(would_return)) {
    throw new Error("invalid would_return");
  }
  if (!isTraderProfile(trader_profile)) {
    throw new Error("invalid trader_profile");
  }
  let note: string | undefined;
  if (raw.note != null && String(raw.note).trim()) {
    note = String(raw.note).trim().slice(0, MAX_NOTE_LEN);
  }
  const page_path =
    raw.page_path != null && String(raw.page_path).trim()
      ? String(raw.page_path).trim().slice(0, 200)
      : "/feedback";
  return { understood, would_return, trader_profile, note, page_path };
}

export function appendFeedback(payload: WebFeedbackSubmitPayload): WebFeedbackEntry {
  ensureDir();
  const entry: WebFeedbackEntry = {
    id: randomUUID(),
    created_at_utc: utcIso(),
    understood: payload.understood,
    would_return: payload.would_return,
    trader_profile: payload.trader_profile,
    note: payload.note?.trim() || null,
    source: "msos_web",
    page_path: payload.page_path ?? "/feedback",
  };
  fs.appendFileSync(feedbackFilePath(), `${JSON.stringify(entry)}\n`, { encoding: "utf-8" });
  return entry;
}

export function listFeedback(limit = 200): WebFeedbackEntry[] {
  const filePath = feedbackFilePath();
  if (!fs.existsSync(filePath)) {
    return [];
  }
  const lines = fs.readFileSync(filePath, "utf-8").split("\n").filter(Boolean);
  const rows: WebFeedbackEntry[] = [];
  for (const line of lines) {
    try {
      rows.push(JSON.parse(line) as WebFeedbackEntry);
    } catch {
      continue;
    }
  }
  rows.sort((a, b) => b.created_at_utc.localeCompare(a.created_at_utc));
  return rows.slice(0, limit);
}
