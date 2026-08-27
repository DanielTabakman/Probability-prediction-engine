import type { HorizonChartPayload, HorizonForwardPoint } from "@/lib/horizonChartPayload";

export const HORIZON_COMPARISON_NO_ADVICE_COPY =
  "Educational comparison only; not financial advice, not a recommendation, and not order execution.";

export type OptionsHorizonComparisonRow = {
  expiry_ts: number;
  expiry_date: string;
  days_out: number;
  target_bucket_days: number[];
  target_bucket_label: string;
  forward_usd: number | null;
  atm_iv_annual: number | null;
  one_sigma_move_usd: number | null;
  trust_flags: string[];
  data_flags: string[];
  time_decay_language: string;
};

export type OptionsHorizonComparisonPayload = {
  schema_version: number;
  kind: "options_horizon_comparison";
  as_of_utc: string;
  target_bucket_days: number[];
  rows: OptionsHorizonComparisonRow[];
  limitations: string[];
  meta: {
    read_only: boolean;
    simulation_only: boolean;
  };
};

const TARGET_BUCKET_DAYS = [30, 60, 90, 180, 365] as const;
const MS_PER_DAY = 24 * 60 * 60 * 1000;

function expiryTs(point: HorizonForwardPoint): number {
  return new Date(point.expiry_utc).getTime();
}

function timeDecayLanguage(daysOut: number, incomplete: boolean): string {
  if (incomplete) return "Time-window comparison only; option quote inputs are incomplete.";
  if (daysOut <= 45) return "Nearer expiry: more time-decay pressure and tighter timing.";
  if (daysOut <= 120) return "Middle expiry: balances time for the view with meaningful decay.";
  return "Longer expiry: more calendar room, with slower daily time decay.";
}

function selectedBuckets(points: { expiryTs: number; daysOut: number }[]): Map<number, number[]> {
  const selected = new Map<number, number[]>();
  for (const target of TARGET_BUCKET_DAYS) {
    const best = [...points].sort((a, b) => {
      const dist = Math.abs(a.daysOut - target) - Math.abs(b.daysOut - target);
      if (dist !== 0) return dist;
      const side = (a.daysOut >= target ? 0 : 1) - (b.daysOut >= target ? 0 : 1);
      if (side !== 0) return side;
      return a.expiryTs - b.expiryTs;
    })[0];
    selected.set(best.expiryTs, [...(selected.get(best.expiryTs) ?? []), target]);
  }
  return selected;
}

export function buildOptionsHorizonComparisonFromChart(
  payload: HorizonChartPayload,
): OptionsHorizonComparisonPayload {
  const asOf = new Date(payload.as_of_utc).getTime();
  const candidates = payload.forward.curve
    .map((point) => ({
      point,
      expiryTs: expiryTs(point),
      daysOut: Math.max(1, Math.ceil((expiryTs(point) - asOf) / MS_PER_DAY)),
    }))
    .filter((row) => Number.isFinite(row.expiryTs) && row.expiryTs > asOf)
    .sort((a, b) => a.expiryTs - b.expiryTs);

  if (!candidates.length) {
    return {
      schema_version: 1,
      kind: "options_horizon_comparison",
      as_of_utc: payload.as_of_utc,
      target_bucket_days: [...TARGET_BUCKET_DAYS],
      rows: [],
      limitations: [
        "No listed future expiries were available for the target buckets.",
        HORIZON_COMPARISON_NO_ADVICE_COPY,
      ],
      meta: { read_only: true, simulation_only: true },
    };
  }

  const bucketMap = selectedBuckets(candidates);
  const selectedExpirySeconds = payload.implied?.expiry_ts ?? null;
  const rows = candidates
    .filter((row) => bucketMap.has(row.expiryTs))
    .map((row) => {
      const isSelected = selectedExpirySeconds === Math.floor(row.expiryTs / 1000);
      const forward = isSelected
        ? payload.implied?.forward_usd ?? row.point.mark_price_usd
        : row.point.mark_price_usd ?? null;
      const atmIv = isSelected ? payload.implied?.atm_iv_annual ?? null : null;
      const dataFlags = [
        ...(atmIv ? [] : ["missing_atm_iv"]),
        ...(forward ? [] : ["missing_forward"]),
        "missing_liquidity",
      ];
      const tYears = Math.max(row.daysOut / 365.25, 1 / 365.25);
      const oneSigma = forward && atmIv ? forward * atmIv * Math.sqrt(tYears) : null;
      const buckets = bucketMap.get(row.expiryTs) ?? [];
      const missingQuoteInputs = !forward || !atmIv;
      return {
        expiry_ts: row.expiryTs,
        expiry_date: row.point.expiry_date,
        days_out: row.daysOut,
        target_bucket_days: buckets,
        target_bucket_label: buckets.map((bucket) => `${bucket}d`).join(" / "),
        forward_usd: forward,
        atm_iv_annual: atmIv,
        one_sigma_move_usd: oneSigma,
        trust_flags: [...(forward ? [] : ["forward_unavailable"]), ...(atmIv ? [] : ["iv_unavailable"])],
        data_flags: dataFlags,
        time_decay_language: timeDecayLanguage(row.daysOut, missingQuoteInputs),
      };
    });

  return {
    schema_version: 1,
    kind: "options_horizon_comparison",
    as_of_utc: payload.as_of_utc,
    target_bucket_days: [...TARGET_BUCKET_DAYS],
    rows,
    limitations: [
      "Rows compare listed expiry windows before expression selection.",
      HORIZON_COMPARISON_NO_ADVICE_COPY,
    ],
    meta: { read_only: true, simulation_only: true },
  };
}
