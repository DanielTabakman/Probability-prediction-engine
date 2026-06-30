import { appendFile, mkdir } from "fs/promises";
import path from "path";
import { randomUUID } from "crypto";

export const PRODUCT_USAGE_FILENAME = "ppe_product_usage.jsonl";

export type ProductUsageRecord = {
  id: string;
  created_at_utc: string;
  event_name: string;
  source?: string;
  path?: string;
  asset_id?: string;
  snapshot_id?: string;
  owner_email?: string;
  review_status?: string;
};

export function productUsageDir(): string {
  const raw = process.env.PPE_PRODUCT_USAGE_DIR?.trim();
  if (raw) return raw;
  return path.join(process.cwd(), "data");
}

export function productUsageFilePath(): string {
  return path.join(productUsageDir(), PRODUCT_USAGE_FILENAME);
}

export async function appendProductUsageEvent(
  payload: Omit<ProductUsageRecord, "id" | "created_at_utc">,
): Promise<ProductUsageRecord> {
  const record: ProductUsageRecord = {
    ...payload,
    id: randomUUID(),
    created_at_utc: new Date().toISOString(),
  };
  const dir = productUsageDir();
  await mkdir(dir, { recursive: true });
  await appendFile(productUsageFilePath(), `${JSON.stringify(record)}\n`, "utf8");
  return record;
}
