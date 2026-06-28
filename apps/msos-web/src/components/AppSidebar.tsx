import Link from "next/link";

import { navItems, secondaryNavItems } from "@/data/commandCenterFixtures";
import { MsosLogo } from "@/components/MsosLogo";
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
        <MsosLogo className="logo" size={32} />
        <div>
          MSOS
          <small>Market Structure OS</small>
        </div>
      </Link>

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

      <div className="sidebar-footer">
        {tier ? (
          <div className="asset on entitlement-badge" data-tier={tier}>
            <span>Account tier</span>
            <span className={`tiny-pill ${tierTone(tier)}`.trim()}>{tierLabel(tier)}</span>
          </div>
        ) : null}

        {showUpgrade ? (
          <Link href={upgradeUrl} className="btn slim primary entitlement-upgrade-link">
            Request upgrade
          </Link>
        ) : null}

        <nav className="sidebar-secondary" aria-label="More">
          <div className="side-label">More</div>
          {secondaryNavItems.map((item) => {
            const active = item.id === activeNavId;
            return (
              <Link
                key={item.id}
                href={item.href}
                className={active ? "active" : undefined}
                aria-current={active ? "page" : undefined}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
