import { NextResponse } from "next/server";

import {
  getOrCreateEntitlement,
  tierLabel,
  upgradeOfferUrl,
} from "@/lib/msosEntitlements";
import { requireProtectedIdentity } from "@/lib/msosIdentity";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const entitlement = getOrCreateEntitlement(identity.email);
    if (!entitlement) {
      return NextResponse.json({ error: "identity required" }, { status: 401 });
    }
    return NextResponse.json({
      ...entitlement,
      tierLabel: tierLabel(entitlement.tier),
      upgradeUrl: upgradeOfferUrl(),
    });
  } catch (err) {
    console.error("entitlements GET failed", err);
    return NextResponse.json({ error: "failed to load entitlement" }, { status: 500 });
  }
}
