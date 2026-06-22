export function ProductWindow() {
  return (
    <section className="product-window" aria-label="Command Center preview">
      <div className="window-head">
        <span className="traffic" />
        <span className="traffic" />
        <span className="traffic" />
        <div className="url">marketstructureos.com / strategy-lab</div>
      </div>
      <div className="window-content">
        <div className="lens-head">
          <div>
            <strong>Strategy Lab</strong>
            <div className="micro">Market read → your view → paper plan</div>
          </div>
          <span className="tag">Live demo</span>
        </div>
        <div className="belief-card">
          <div className="micro">YOU VS THE MARKET</div>
          <div className="belief-grid">
            <div className="small-panel">
              <div className="k">Options imply</div>
              <div className="v amber">Wider range</div>
              <div className="micro">From Deribit quotes</div>
            </div>
            <div className="small-panel">
              <div className="k">Your view</div>
              <div className="v teal">Tighter range</div>
              <div className="micro">Less vol than priced</div>
            </div>
          </div>
          <div className="compare">
            <div className="bar market" />
            <div className="micro">vs</div>
            <div className="bar" />
          </div>
          <div className="callout">
            <div>
              <div className="micro">GAP</div>
              <div className="delta">21%</div>
            </div>
            <div>
              <span className="tag amber">Worth a look</span>
              <div className="micro" style={{ marginTop: 9 }}>
                You expect about 21% less movement than options price
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
