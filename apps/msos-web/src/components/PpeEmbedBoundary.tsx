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
};

type DisplayPayload = {
  kind: string;
  spot_usd: number;
  series_by_expiry: DisplaySeries[];
};

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
    const data = (await res.json()) as DisplayPayload;
    if (data?.kind !== "distribution_display_boundary") {
      return null;
    }
    if (!data.series_by_expiry?.length) {
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
  );
}

export async function PpeEmbedBoundary() {
  const payload = await loadDisplayPayload();

  if (payload) {
    const primary = payload.series_by_expiry[0];
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
            <li>Primary: display payload at <code>/ppe-display-api/display.json</code></li>
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
