export function ProductWindow() {
  return (
    <section className="product-window" aria-label="Command Center preview">
      <div className="window-head">
        <span className="traffic" />
        <span className="traffic" />
        <span className="traffic" />
        <div className="url">marketstructureos.com / command-center</div>
      </div>
      <div className="window-content">
        <div className="lens-head">
          <div>
            <strong>Command Center</strong>
            <div className="micro">
              Compare the market&apos;s view with yours — then find the cleanest expression.
            </div>
          </div>
          <span className="tag">Live demo</span>
        </div>
        <div className="belief-card">
          <div className="micro">Market comparison</div>
          <div className="belief-grid">
            <div className="small-panel">
              <div className="k">Market implies</div>
              <div className="v amber">Wider expected range</div>
              <div className="micro">Options-implied distribution</div>
            </div>
            <div className="small-panel">
              <div className="k">Your thesis</div>
              <div className="v teal">Narrower expected range</div>
              <div className="micro">Your stated market view</div>
            </div>
          </div>
          <div className="compare">
            <div className="bar market" />
            <div className="micro">vs</div>
            <div className="bar" />
          </div>
          <div className="callout">
            <div>
              <div className="micro">Thesis gap</div>
              <div className="delta">21%</div>
            </div>
            <div>
              <span className="tag amber">Worth reviewing</span>
              <div className="micro" style={{ marginTop: 9 }}>
                Your range is 21% narrower than current options pricing implies.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
