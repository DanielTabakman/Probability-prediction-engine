import Link from "next/link";

import { connectedMarkets, navItems } from "@/data/commandCenterFixtures";
import type { EntitlementTier } from "@/lib/msosEntitlements";
import { tierLabel, upgradeOfferUrl } from "@/lib/msosEntitlements";
import { MSOS_ROUTES } from "@/lib/msosPublicUrls";

type AppSidebarProps = {
  activeNavId?: string;
  tier?: EntitlementTier | null;
};

function tierTone(tier: EntitlementTier): string {
  if (tier === "paid") return "teal";
  if (tier === "research_beta") return "amber";
  return "";
}

export function AppSidebar({ activeNavId = "command-center", tier = null }: AppSidebarProps) {
  const upgradeUrl = upgradeOfferUrl();
  const showUpgrade = tier === "free" && upgradeUrl;

  return (
    <aside className="app-sidebar">
      <Link className="brand app-brand" href={MSOS_ROUTES.home}>
        <div className="logo" aria-hidden="true" />
        <div>
          MSOS
          <small>Market Structure OS</small>
        </div>
      </Link>

      {tier ? (
        <div className="asset on entitlement-badge" data-tier={tier}>
          <span>Account tier</span>
          <span className={`tiny-pill ${tierTone(tier)}`.trim()}>{tierLabel(tier)}</span>
        </div>
      ) : null}

      {showUpgrade ? (
        <Link href={upgradeUrl} className="btn slim primary entitlement-upgrade-link">
          Upgrade
        </Link>
      ) : null}

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
    </aside>
  );
}
