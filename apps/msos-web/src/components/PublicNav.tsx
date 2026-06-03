import Link from "next/link";

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
          <Link className="btn slim primary" href="/command-center">
            Enter Command Center
          </Link>
        </div>
      </div>
    </nav>
  );
}
