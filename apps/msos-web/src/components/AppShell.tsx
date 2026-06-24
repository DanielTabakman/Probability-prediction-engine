import { headers } from "next/headers";

import { AppSidebar } from "@/components/AppSidebar";
import { getOrCreateEntitlement } from "@/lib/msosEntitlements";
import { resolveMsosIdentityFromHeaders } from "@/lib/msosIdentityCore";

type AppShellProps = {
  children: React.ReactNode;
  activeNavId?: string;
};

export async function AppShell({ children, activeNavId }: AppShellProps) {
  const requestHeaders = await headers();
  const ownerEmail = resolveMsosIdentityFromHeaders(requestHeaders);
  const entitlement = ownerEmail ? getOrCreateEntitlement(ownerEmail) : null;

  return (
    <div className="app-shell">
      <AppSidebar activeNavId={activeNavId} tier={entitlement?.tier ?? null} />
      <div className="app-main">{children}</div>
    </div>
  );
}
