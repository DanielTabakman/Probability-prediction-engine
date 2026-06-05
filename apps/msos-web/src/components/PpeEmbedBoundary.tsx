/**
 * PPE embed boundary (P4) — display/proxy only; no distribution math in TypeScript.
 * Platform slice wires Caddy reverse proxy; until then iframe URL comes from env or shows degraded state.
 */

const PPE_EMBED_URL = (process.env.NEXT_PUBLIC_PPE_EMBED_URL ?? "").trim();

export function PpeEmbedBoundary() {
  if (!PPE_EMBED_URL) {
    return (
      <div className="ppe-embed ppe-embed-degraded" role="region" aria-label="PPE implied lab embed">
        <div className="ppe-embed-placeholder">
          <span className="tag amber">Embed pending</span>
          <h3>PPE implied lab surface</h3>
          <p>
            Streamlit upstream will load here once the platform proxy is wired (MSOS P4 platform slice).
            Fixture preview below — authoritative math stays in Python / Streamlit.
          </p>
          <ul className="ppe-embed-notes">
            <li>Primary path: Caddy reverse proxy per stack ADR</li>
            <li>Fallback: iframe to authenticated Streamlit host if proxy blocked</li>
            <li>Trust/degraded states surface when upstream is unavailable</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="ppe-embed" role="region" aria-label="PPE implied lab embed">
      <iframe
        title="PPE Strategy Lab — options distribution lens"
        src={PPE_EMBED_URL}
        className="ppe-embed-frame"
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </div>
  );
}
