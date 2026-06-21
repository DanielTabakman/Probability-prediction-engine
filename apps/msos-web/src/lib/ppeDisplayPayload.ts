/**
 * Read-only PPE display payload (pre-computed in Python). No distribution math here.
 */

export const PPE_DISPLAY_API_URL = (
  process.env.NEXT_PUBLIC_PPE_DISPLAY_API_URL ?? "/ppe-display-api/display.json"
).trim();

export const PPE_EMBED_ONLY_PARAM = "embed_only";

export const PPE_EMBED_URL = (process.env.NEXT_PUBLIC_PPE_EMBED_URL ?? "").trim();

export type DisplaySeries = {
  expiry_date: string;
  prices_usd: number[];
  pdf_pct: number[];
  mean_usd?: number;
  quartiles_usd?: {
    q1_usd: number;
    median_usd: number;
    q3_usd: number;
  };
};

export type DisplaySummaryRow = Record<string, string>;

export type DisplayPayload = {
  kind: string;
  spot_usd: number;
  as_of_utc?: string;
  series_by_expiry: DisplaySeries[];
  summary?: {
    table_rows?: DisplaySummaryRow[];
  };
};

export type LabMetric = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export type LabOutcomeSummary = {
  tag: string;
  tagTone: "teal" | "amber";
  delta: string;
  headline: string;
  body: string;
  scores: { label: string; value: string; tone: "teal" | "amber" }[];
};

function isNumberArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.length > 1 && value.every((item) => typeof item === "number");
}

export function isDisplaySeries(value: unknown): value is DisplaySeries {
  if (!value || typeof value !== "object") {
    return false;
  }
  const series = value as Partial<DisplaySeries>;
  return (
    typeof series.expiry_date === "string" &&
    isNumberArray(series.prices_usd) &&
    isNumberArray(series.pdf_pct) &&
    series.prices_usd.length === series.pdf_pct.length
  );
}

export function isDisplayPayload(value: unknown): value is DisplayPayload {
  if (!value || typeof value !== "object") {
    return false;
  }
  const payload = value as Partial<DisplayPayload>;
  return (
    payload.kind === "distribution_display_boundary" &&
    typeof payload.spot_usd === "number" &&
    Array.isArray(payload.series_by_expiry) &&
    payload.series_by_expiry.some(isDisplaySeries)
  );
}

export function formatUsd(value: number): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
    style: "currency",
    currency: "USD",
  }).format(value);
}

function primaryLognormalRow(payload: DisplayPayload): DisplaySummaryRow | undefined {
  const rows = payload.summary?.table_rows ?? [];
  return rows.find((row) => {
    const method = (row.Method ?? row.method ?? "").toLowerCase();
    return method.includes("lognormal") || method.includes("reference");
  });
}

export function buildLabMetricsFromPayload(payload: DisplayPayload): LabMetric[] {
  const primary = payload.series_by_expiry.find(isDisplaySeries);
  const lognormal = primaryLognormalRow(payload);
  const marketWidth = lognormal?.["Implied range width (IQR)"] ?? "—";
  const median = lognormal?.["Median terminal price (50th %)"] ?? "—";

  return [
    { label: "Selected market", value: "BTC / Options" },
    { label: "Expiry", value: primary?.expiry_date ?? "—" },
    { label: "Spot", value: formatUsd(payload.spot_usd) },
    { label: "Market width (IQR)", value: marketWidth, tone: "amber" },
    { label: "Market median", value: median, tone: "teal" },
    { label: "Data", value: "Live via PPE", tone: "teal" },
  ];
}

export function buildOutcomeFromPayload(payload: DisplayPayload): LabOutcomeSummary {
  const lognormal = primaryLognormalRow(payload);
  const marketWidth = lognormal?.["Implied range width (IQR)"] ?? "the market-implied range";
  const mean = lognormal?.["Risk-neutral mean"] ?? "—";

  return {
    tag: "Live read",
    tagTone: "teal",
    delta: "—",
    headline: "Market-implied distribution is loaded from PPE.",
    body: `Options-implied summary for the selected expiry: mean ${mean}, interquartile width ${marketWidth}. Set your belief below and confirm when ready — thesis controls are still a guided draft on this pass.`,
    scores: [
      { label: "Market view", value: "From Deribit", tone: "amber" },
      { label: "Your thesis", value: "Draft — confirm next", tone: "teal" },
      { label: "Materiality", value: "Inspect after confirm", tone: "teal" },
      { label: "Trust", value: "Live feed", tone: "teal" },
    ],
  };
}

/** Server-side fetch target (Docker internal); browser uses public relative path. */
function resolveDisplayApiFetchUrl(): string {
  const serverUrl = process.env.PPE_DISPLAY_API_SERVER_URL?.trim();
  if (serverUrl) {
    return serverUrl;
  }
  return PPE_DISPLAY_API_URL;
}

export async function fetchDisplayPayload(): Promise<DisplayPayload | null> {
  const fetchUrl = resolveDisplayApiFetchUrl();
  if (!fetchUrl) {
    return null;
  }
  try {
    const res = await fetch(fetchUrl, { cache: "no-store" });
    if (!res.ok) {
      return null;
    }
    const data: unknown = await res.json();
    if (!isDisplayPayload(data)) {
      return null;
    }
    return data;
  } catch {
    return null;
  }
}
