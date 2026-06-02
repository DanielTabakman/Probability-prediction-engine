export function ProductWindow() {
  return (
    <section className="product-window" aria-label="Command Center preview">
      <div className="window-head">
        <span className="traffic" />
        <span className="traffic" />
        <span className="traffic" />
        <div className="url">app.marketstructureos.com / command-center</div>
      </div>
      <div className="window-content">
        <div className="lens-head">
          <div>
            <strong>Command Center</strong>
            <div className="micro">Read surfaces → state thesis → fit expression → learn</div>
          </div>
          <span className="tag">Preview</span>
        </div>
        <div className="belief-card">
          <div className="micro">MARKET SURFACE COMPARISON</div>
          <div className="belief-grid">
            <div className="small-panel">
              <div className="k">Market implies</div>
              <div className="v amber">Wider range</div>
              <div className="micro">Options distribution lens</div>
            </div>
            <div className="small-panel">
              <div className="k">Your thesis</div>
              <div className="v teal">Narrower range</div>
              <div className="micro">Human-defined belief</div>
            </div>
          </div>
          <div className="compare">
            <div className="bar market" />
            <div className="micro">vs</div>
            <div className="bar" />
          </div>
          <div className="callout">
            <div>
              <div className="micro">DISAGREEMENT LOCATED</div>
              <div className="delta">21%</div>
            </div>
            <div>
              <span className="tag amber">Worth inspecting</span>
              <div className="micro" style={{ marginTop: 9 }}>
                Your range is 21% narrower than market pricing
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
