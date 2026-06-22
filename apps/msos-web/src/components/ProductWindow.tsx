import { homepagePreview } from "@/content/homepage";

export function ProductWindow() {
  const preview = homepagePreview;

  return (
    <section className="product-window" aria-label="Command Center preview">
      <div className="window-head">
        <span className="traffic" />
        <span className="traffic" />
        <span className="traffic" />
        <div className="url">{preview.urlLabel}</div>
      </div>
      <div className="window-content">
        <div className="lens-head">
          <div>
            <strong>{preview.title}</strong>
            <div className="micro">{preview.subtitle}</div>
          </div>
          <span className="tag">{preview.demoTag}</span>
        </div>
        <div className="belief-card">
          <div className="micro">{preview.comparisonSection}</div>
          <div className="belief-grid">
            <div className="small-panel">
              <div className="k">{preview.marketImplies.label}</div>
              <div className="v amber">{preview.marketImplies.value}</div>
              <div className="micro">{preview.marketImplies.hint}</div>
            </div>
            <div className="small-panel">
              <div className="k">{preview.yourThesis.label}</div>
              <div className="v teal">{preview.yourThesis.value}</div>
              <div className="micro">{preview.yourThesis.hint}</div>
            </div>
          </div>
          <div className="compare">
            <div className="bar market" />
            <div className="micro">{preview.vs}</div>
            <div className="bar" />
          </div>
          <div className="callout">
            <div>
              <div className="micro">{preview.thesisGap.label}</div>
              <div className="delta">{preview.thesisGap.value}</div>
            </div>
            <div>
              <span className="tag amber">{preview.thesisGap.tag}</span>
              <div className="micro" style={{ marginTop: 9 }}>
                {preview.thesisGap.detail}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
