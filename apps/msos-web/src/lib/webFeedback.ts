import { appendFile, mkdir, readFile } from "fs/promises";
import path from "path";
import { randomUUID } from "crypto";

export const WEB_FEEDBACK_FILENAME = "ppe_web_feedback.jsonl";

export type WebFeedbackRecord = {
  id: string;
  created_at_utc: string;
  source: string;
  tester_profile?: string;
  comprehension?: string;
  thesis_confirm?: string;
  return_intent?: string;
  paid_interest?: string;
  confusion_category?: string;
  usefulness?: number;
  repeat_use_intent?: number;
  objections_text?: string;
  session_note?: string;
  reality_check_row?: string;
  session_started_at?: string;
};

export function feedbackDir(): string {
  const raw = process.env.PPE_WEB_FEEDBACK_DIR?.trim();
  if (raw) return raw;
  return path.join(process.cwd(), "data");
}

export function feedbackFilePath(): string {
  return path.join(feedbackDir(), WEB_FEEDBACK_FILENAME);
}

export async function appendWebFeedback(
  payload: Omit<WebFeedbackRecord, "id" | "created_at_utc">
): Promise<WebFeedbackRecord> {
  const record: WebFeedbackRecord = {
    ...payload,
    id: randomUUID(),
    created_at_utc: new Date().toISOString(),
  };
  const dir = feedbackDir();
  await mkdir(dir, { recursive: true });
  await appendFile(feedbackFilePath(), `${JSON.stringify(record)}\n`, "utf8");
  return record;
}

export async function readWebFeedbackRecords(limit = 200): Promise<WebFeedbackRecord[]> {
  const pathToFile = feedbackFilePath();
  let raw = "";
  try {
    raw = await readFile(pathToFile, "utf8");
  } catch {
    return [];
  }
  const records: WebFeedbackRecord[] = [];
  for (const line of raw.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      const row = JSON.parse(trimmed) as WebFeedbackRecord;
      if (row && typeof row === "object" && row.id) {
        records.push(row);
      }
    } catch {
      continue;
    }
  }
  records.sort((a, b) => String(b.created_at_utc).localeCompare(String(a.created_at_utc)));
  return records.slice(0, limit);
}
