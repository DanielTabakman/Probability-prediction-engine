/**
 * Region Bet session resume v1 — restore the current owner's most recent
 * valid paper workflow without guessing or leaking another owner's state.
 */

import { normalizeOwnerEmail } from "@/lib/msosIdentityCore";
import { scopeOwnerId } from "@/lib/msosSession";
import {
  isRegionBetContract,
  saveRegionBet,
  type RegionBetContract,
} from "@/lib/regionBet";
import {
  resolveRegionBetGuidedShellResumeStep,
  type RegionBetGuidedShellStep,
} from "@/lib/regionBetGuidedShell";

export const REGION_BET_RESUME_KIND = "region_bet_session_resume";

export const REGION_BET_RESUME_STALE_STATUSES = ["closed", "archived"] as const;

export const REGION_BET_RESUME_LIMITATION =
  "Paper workflow only. Resume restores your saved Region Bet. Not financial advice, not a recommendation, and not order execution.";

export const REGION_BET_RESUME_CLEAN_START_COPY =
  "No valid saved Region Bet for this owner. Start a clean paper draft instead of substituting another workspace.";

export type RegionBetResumeMode = "resume" | "clean_start";

export type RegionBetResumeReason =
  | "valid"
  | "malformed"
  | "cross_owner"
  | "stale"
  | "missing";

export type RegionBetResumeState = {
  schema_version: 1;
  kind: typeof REGION_BET_RESUME_KIND;
  mode: RegionBetResumeMode;
  reason: RegionBetResumeReason;
  regionBet: RegionBetContract | null;
  step: RegionBetGuidedShellStep;
  clean_start_available: true;
  paper_only: true;
  limitation: string;
};

export type ResolveRegionBetResumeInput = {
  requestOwner: string;
  storedOwner?: string | null;
  stored: unknown;
  storedStep?: unknown;
};

export function regionBetResumeOwnerKey(raw: string | null | undefined): string {
  const scoped = scopeOwnerId(raw);
  if (scoped?.startsWith("session:")) return scoped;
  return normalizeOwnerEmail(raw) ?? "__anon__";
}

export function regionBetResumeOwnersMatch(
  storedOwner: string | null | undefined,
  requestOwner: string,
): boolean {
  return regionBetResumeOwnerKey(storedOwner) === regionBetResumeOwnerKey(requestOwner);
}

export function isRegionBetResumeStale(regionBet: RegionBetContract): boolean {
  if (
    regionBet.lifecycle.status === "closed" ||
    regionBet.lifecycle.status === "archived"
  ) {
    return true;
  }
  if (typeof regionBet.lifecycle.closed_at_utc === "string") {
    return true;
  }
  return Number.isNaN(Date.parse(regionBet.lifecycle.updated_at_utc));
}

export function createCleanStartRegionBetResume(
  reason: RegionBetResumeReason,
): RegionBetResumeState {
  return {
    schema_version: 1,
    kind: REGION_BET_RESUME_KIND,
    mode: "clean_start",
    reason,
    regionBet: null,
    step: "asset",
    clean_start_available: true,
    paper_only: true,
    limitation: REGION_BET_RESUME_LIMITATION,
  };
}

export function resolveRegionBetResume(
  input: ResolveRegionBetResumeInput,
): RegionBetResumeState {
  if (input.stored == null) {
    return createCleanStartRegionBetResume("missing");
  }
  if (!regionBetResumeOwnersMatch(input.storedOwner, input.requestOwner)) {
    return createCleanStartRegionBetResume("cross_owner");
  }
  if (!isRegionBetContract(input.stored)) {
    return createCleanStartRegionBetResume("malformed");
  }
  if (isRegionBetResumeStale(input.stored)) {
    return createCleanStartRegionBetResume("stale");
  }
  const storedStep =
    input.storedStep !== undefined ? input.storedStep : input.stored.guided_step;
  return {
    schema_version: 1,
    kind: REGION_BET_RESUME_KIND,
    mode: "resume",
    reason: "valid",
    regionBet: input.stored,
    step: resolveRegionBetGuidedShellResumeStep(storedStep, input.stored),
    clean_start_available: true,
    paper_only: true,
    limitation: REGION_BET_RESUME_LIMITATION,
  };
}

export function isRegionBetResumeState(value: unknown): value is RegionBetResumeState {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  const mode = row.mode;
  const reason = row.reason;
  const regionBet = row.regionBet;
  if (row.schema_version !== 1 || row.kind !== REGION_BET_RESUME_KIND) return false;
  if (mode !== "resume" && mode !== "clean_start") return false;
  if (
    reason !== "valid" &&
    reason !== "malformed" &&
    reason !== "cross_owner" &&
    reason !== "stale" &&
    reason !== "missing"
  ) {
    return false;
  }
  if (row.clean_start_available !== true || row.paper_only !== true) return false;
  if (typeof row.limitation !== "string") return false;
  if (mode === "clean_start") {
    return regionBet === null && row.step === "asset";
  }
  return (
    isRegionBetContract(regionBet) &&
    typeof row.step === "string" &&
    resolveRegionBetGuidedShellResumeStep(row.step, regionBet) === row.step
  );
}

export function regionBetResumeRestoredFields(regionBet: RegionBetContract): {
  asset_id: string;
  expiry_utc: string;
  window_start_utc?: string;
  window_end_utc?: string;
  selected_region: RegionBetContract["selected_region"];
  selected_expression_ref: RegionBetContract["selected_expression_ref"];
} {
  return {
    asset_id: regionBet.asset.asset_id,
    expiry_utc: regionBet.target.expiry_utc,
    window_start_utc: regionBet.target.window_start_utc,
    window_end_utc: regionBet.target.window_end_utc,
    selected_region: { ...regionBet.selected_region },
    selected_expression_ref: regionBet.selected_expression_ref
      ? { ...regionBet.selected_expression_ref }
      : null,
  };
}

export async function fetchRegionBetResume(): Promise<RegionBetResumeState> {
  if (typeof window === "undefined") {
    return createCleanStartRegionBetResume("missing");
  }
  try {
    const response = await fetch("/api/theses/region-bet?resume=1", {
      cache: "no-store",
      credentials: "include",
    });
    if (!response.ok) {
      return createCleanStartRegionBetResume("missing");
    }
    const payload = (await response.json()) as { resume?: unknown };
    if (!isRegionBetResumeState(payload.resume)) {
      return createCleanStartRegionBetResume("malformed");
    }
    if (payload.resume.mode === "resume" && payload.resume.regionBet) {
      saveRegionBet(payload.resume.regionBet);
    }
    return payload.resume;
  } catch {
    return createCleanStartRegionBetResume("missing");
  }
}
