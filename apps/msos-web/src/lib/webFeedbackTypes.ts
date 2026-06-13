/** Public web feedback schema (MSOS + export scripts). */

export const TRADER_PROFILES = [
  "btc_options",
  "crypto_vol",
  "equities",
  "exploring",
] as const;

export type TraderProfile = (typeof TRADER_PROFILES)[number];

export const TRADER_PROFILE_LABELS: Record<TraderProfile, string> = {
  btc_options: "BTC options",
  crypto_vol: "Other crypto vol",
  equities: "Equities / stock options",
  exploring: "Just exploring",
};

export type UnderstoodAnswer = "yes" | "not_yet";
export type WouldReturnAnswer = "yes" | "no";

export type WebFeedbackEntry = {
  id: string;
  created_at_utc: string;
  understood: UnderstoodAnswer;
  would_return: WouldReturnAnswer;
  trader_profile: TraderProfile;
  note: string | null;
  source: "msos_web";
  page_path: string;
};

export type WebFeedbackSubmitPayload = {
  understood: UnderstoodAnswer;
  would_return: WouldReturnAnswer;
  trader_profile: TraderProfile;
  note?: string;
  page_path?: string;
};
