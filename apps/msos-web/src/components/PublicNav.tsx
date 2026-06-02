export function PublicNav() {
  return (
    <nav className="public-nav">
      <div className="brand">
        <div className="logo" aria-hidden="true" />
        <div>
          Market Structure OS
          <small>Probability &amp; thesis intelligence</small>
        </div>
      </div>
      <div className="nav-links">
        <span className="sel">Platform</span>
        <span>Strategy Lab</span>
        <span>Market surfaces</span>
        <span>Vision</span>
        <div className="nav-actions">
          <span className="btn slim dark">Sign in</span>
          <span className="btn slim primary">Enter Command Center</span>
        </div>
      </div>
    </nav>
  );
}
