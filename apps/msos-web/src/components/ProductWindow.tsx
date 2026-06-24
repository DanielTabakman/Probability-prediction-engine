import Link from "next/link";

import { MSOS_ROUTES } from "@/lib/msosPublicUrls";

export function ProductWindow() {
  return (
    <Link className="product-window product-window-link" href={MSOS_ROUTES.strategyLab}>
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
            <div className="micro">Purple market curve vs your teal belief — click to open live demo.</div>
          </div>
          <span className="tag">Live</span>
        </div>
        <div className="belief-card">
          <div className="micro">Market comparison</div>
          <div className="belief-grid">
            <div className="small-panel">
              <div className="k">Market implies</div>
              <div className="v amber">Lognormal from chain</div>
            </div>
            <div className="small-panel">
              <div className="k">Your view</div>
              <div className="v teal">Adjust with buttons</div>
            </div>
          </div>
          <div className="compare">
            <div className="bar market" />
            <div className="micro">vs</div>
            <div className="bar" />
          </div>
        </div>
      </div>
    </Link>
  );
}
