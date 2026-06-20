/**
 * PPE embed boundary — display/proxy only; no distribution math in TypeScript.
 * Primary: read-only display payload (pre-computed series from Python).
 * Fallback: chromeless Streamlit embed (`?embed_only=1`) — no nested app chrome.
 */

export const PPE_EMBED_ANCHOR_ID = "distribution-summary";
export const PPE_EMBED_ONLY_PARAM = "embed_only";

const PPE_EMBED_URL = (process.env.NEXT_PUBLIC_PPE_EMBED_URL ?? "").trim();
const PPE_DISPLAY_API_URL = (
  process.env.NEXT_PUBLIC_PPE_DISPLAY_API_URL ?? "/ppe-display-api/display.json"
).trim();

type DisplaySeries = {
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

type DisplayPayload = {
  kind: string;
  spot_usd: number;
  series_by_expiry: DisplaySeries[];
};

function isNumberArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.length > 1 && value.every((item) => typeof item === "number");
}

function isDisplaySeries(value: unknown): value is DisplaySeries {
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

function isDisplayPayload(value: unknown): value is DisplayPayload {
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

function formatUsd(value: number): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
    style: "currency",
    currency: "USD",
  }).format(value);
}

function buildChromelessEmbedSrc(baseUrl: string): string {
  const withoutHash = baseUrl.replace(/#.*$/, "");
  const [path, query = ""] = withoutHash.split("?");
  const params = new URLSearchParams(query);
  params.set(PPE_EMBED_ONLY_PARAM, "1");
  const qs = params.toString();
  return qs ? `${path}?${qs}` : `${path}?${PPE_EMBED_ONLY_PARAM}=1`;
}

/** Map pre-computed price/pdf arrays to SVG path (linear scale only — no new math). */
function seriesToSvgPath(
  prices: number[],
  pdf: number[],
  width: number,
  height: number,
  pad: number,
): string {
  if (!prices.length || prices.length !== pdf.length) {
    return "";
  }
  const xMin = prices[0];
  const xMax = prices[prices.length - 1];
  const xSpan = xMax - xMin || 1;
  const yMax = Math.max(...pdf, 1);
  const innerW = width - pad * 2;
  const innerH = height - pad * 2;
  const points = prices.map((price, index) => {
    const x = pad + ((price - xMin) / xSpan) * innerW;
    const y = pad + innerH - (pdf[index] / yMax) * innerH;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return `M ${points.join(" L ")}`;
}

async function loadDisplayPayload(): Promise<DisplayPayload | null> {
  if (!PPE_DISPLAY_API_URL) {
    return null;
  }
  try {
    const res = await fetch(PPE_DISPLAY_API_URL, { cache: "no-store" });
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

function NativeDistributionChart({ series, spotUsd }: { series: DisplaySeries; spotUsd: number }) {
  const path = seriesToSvgPath(series.prices_usd, series.pdf_pct, 700, 280, 20);
  const spotX =
    series.prices_usd.length > 1
      ? 20 +
        ((spotUsd - series.prices_usd[0]) /
          (series.prices_usd[series.prices_usd.length - 1] - series.prices_usd[0] || 1)) *
          660
      : 350;

  return (
    <>
      <div className="graph" role="img" aria-label={`Distribution curve for ${series.expiry_date}`}>
        <svg viewBox="0 0 700 280" preserveAspectRatio="none">
          <path
            d={`${path} L 680,250 L 20,250 Z`}
            stroke="#9e8bff"
            strokeWidth="4"
            fill="rgba(158, 139, 255, 0.14)"
          />
          <line x1={spotX} y1="38" x2={spotX} y2="250" stroke="#233c55" strokeDasharray="5 8" />
          <text x={spotX + 4} y="54" fill="#8ea4bd" fontSize="12">
            spot
          </text>
        </svg>
      </div>
      {series.mean_usd !== undefined && series.quartiles_usd ? (
        <div className="ppe-summary-table" aria-label="PPE display payload summary">
          <span>Mean {formatUsd(series.mean_usd)}</span>
          <span>Q1 {formatUsd(series.quartiles_usd.q1_usd)}</span>
          <span>Median {formatUsd(series.quartiles_usd.median_usd)}</span>
          <span>Q3 {formatUsd(series.quartiles_usd.q3_usd)}</span>
        </div>
      ) : null}
    </>
  );
}

export async function PpeEmbedBoundary() {
  const payload = await loadDisplayPayload();

  if (payload) {
    const primary = payload.series_by_expiry.find(isDisplaySeries);
    if (!primary) {
      return null;
    }
    return (
      <div className="ppe-chart-region" role="region" aria-label="PPE distribution chart region">
        <p className="ppe-embed-live-note">
          <span className="tag teal">Live via PPE</span> Native chart from read-only display payload —
          distribution math stays in Python.
        </p>
        <NativeDistributionChart series={primary} spotUsd={payload.spot_usd} />
      </div>
    );
  }

  if (!PPE_EMBED_URL) {
    return (
      <div className="ppe-embed ppe-embed-degraded" role="region" aria-label="PPE implied lab embed">
        <div className="ppe-embed-placeholder">
          <span className="tag amber">Embed pending</span>
          <h3>PPE distribution chart region</h3>
          <p>
            Chart loads from the read-only display API or a chromeless PPE embed once platform wiring
            is live. MSOS owns the shell; Python owns all distribution math.
          </p>
          <ul className="ppe-embed-notes">
            <li>
              Primary: display payload at <code>/ppe-display-api/display.json</code> with
              pre-computed <code>prices_usd</code>, <code>pdf_pct</code>, <code>mean_usd</code>, and
              <code>quartiles_usd</code>
            </li>
            <li>Fallback: chromeless embed with <code>?{PPE_EMBED_ONLY_PARAM}=1</code></li>
            <li>Degraded states surface when upstream is unavailable</li>
          </ul>
        </div>
      </div>
    );
  }

  const embedSrc = buildChromelessEmbedSrc(PPE_EMBED_URL);

  return (
    <div className="ppe-embed ppe-embed-chromeless" role="region" aria-label="PPE chromeless embed">
      <p className="ppe-embed-live-note">
        <span className="tag teal">Live via PPE</span> Chromeless embed — distribution summary and
        chart only (<code>?{PPE_EMBED_ONLY_PARAM}=1</code>), no nested Streamlit chrome.
      </p>
      <iframe
        title="PPE Strategy Lab — chromeless distribution view"
        src={embedSrc}
        className="ppe-embed-frame ppe-embed-frame-chromeless"
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </div>
  );
}
