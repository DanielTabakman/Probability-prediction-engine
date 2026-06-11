/**
 * PPE embed boundary (P4) — display/proxy only; no distribution math in TypeScript.
 * Platform slice wires Caddy reverse proxy; until then iframe URL comes from env or shows degraded state.
 *
 * Embed anchor: append `#distribution-summary` so the Streamlit implied lab scrolls to the
 * labeled Distribution summary table (see `DIST_SUMMARY_ANCHOR_ID` in Python `implied_lab_legibility.py`).
 */

/** Streamlit anchor id for the on-screen Distribution summary table (Python canon). */
export const PPE_EMBED_ANCHOR_ID = "distribution-summary";

const PPE_EMBED_URL = (process.env.NEXT_PUBLIC_PPE_EMBED_URL ?? "").trim();

function buildEmbedSrc(baseUrl: string): string {
  const trimmed = baseUrl.replace(/#.*$/, "").replace(/\/$/, "");
  return `${trimmed}#${PPE_EMBED_ANCHOR_ID}`;
}

export function PpeEmbedBoundary() {
  if (!PPE_EMBED_URL) {
    return (
      <div className="ppe-embed ppe-embed-degraded" role="region" aria-label="PPE implied lab embed">
        <div className="ppe-embed-placeholder">
          <span className="tag amber">Embed pending</span>
          <h3>PPE implied lab — Distribution summary</h3>
          <p>
            Live Streamlit loads here once the platform proxy is wired (MSOS platform slice). The embed
            opens at the labeled <strong>Distribution summary</strong> table — mean and quartiles across
            expiries, computed in Python only.
          </p>
          <ul className="ppe-embed-notes">
            <li>Primary path: Caddy reverse proxy per stack ADR</li>
            <li>Fragment: <code>#{PPE_EMBED_ANCHOR_ID}</code> scrolls to the summary table</li>
            <li>Trust/degraded states surface when upstream is unavailable</li>
          </ul>
        </div>
      </div>
    );
  }

  const embedSrc = buildEmbedSrc(PPE_EMBED_URL);

  return (
    <div className="ppe-embed" role="region" aria-label="PPE implied lab embed">
      <p className="ppe-embed-live-note">
        <span className="tag teal">Live via PPE</span> Embedded implied lab — scrolls to Distribution
        summary (<code>#{PPE_EMBED_ANCHOR_ID}</code>).
      </p>
      <iframe
        title="PPE Strategy Lab — distribution summary"
        src={embedSrc}
        className="ppe-embed-frame"
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </div>
  );
}
