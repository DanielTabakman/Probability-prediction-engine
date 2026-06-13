import Link from "next/link";

import { connectedMarkets, navItems } from "@/data/commandCenterFixtures";

type AppSidebarProps = {
  activeNavId?: string;
};

export function AppSidebar({ activeNavId = "command-center" }: AppSidebarProps) {
  return (
    <aside className="app-sidebar">
      <div className="brand app-brand">
        <div className="logo" aria-hidden="true" />
        <div>
          MSOS
          <small>Market Structure OS</small>
        </div>
      </div>

      <nav className="menu" aria-label="Workspace">
        {navItems.map((item) => {
          const active = item.id === activeNavId;
          const className = active ? "active" : item.disabled ? "disabled" : undefined;
          if (item.disabled) {
            return (
              <span key={item.id} className={className} aria-disabled="true">
                <span className="ico" aria-hidden="true" />
                {item.label}
              </span>
            );
          }
          return (
            <Link key={item.id} href={item.href} className={className} aria-current={active ? "page" : undefined}>
              <span className="ico" aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="side-label">Connected markets</div>
      {connectedMarkets.map((asset) => (
        <div key={asset.label} className={`asset ${asset.live ? "on" : "off"}`}>
          <span>{asset.label}</span>
          {asset.live ? <span className="tiny-pill">{asset.status}</span> : <span>{asset.status}</span>}
        </div>
      ))}

      <div className="side-label">System</div>
      <div className="asset on">
        <span>Trust state</span>
        <span className="teal">Good</span>
      </div>
      <Link href="/feedback" className="side-feedback-link">
        Give feedback
      </Link>
    </aside>
  );
}
