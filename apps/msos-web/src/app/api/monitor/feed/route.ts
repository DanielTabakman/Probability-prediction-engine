import { NextResponse } from "next/server";

import {
  DISPLAY_CURRENCY_COOKIE,
  parseDisplayCurrencyFromCookie,
} from "@/lib/displayCurrency";
import { loadMonitorFeed } from "@/lib/monitorHistoryFeed";
import { requireProtectedIdentity } from "@/lib/msosIdentity";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const cookieHeader = request.headers.get("cookie") ?? "";
    const match = cookieHeader.match(new RegExp(`${DISPLAY_CURRENCY_COOKIE}=([^;]+)`));
    const displayCurrency = parseDisplayCurrencyFromCookie(match?.[1]);
    const feed = await loadMonitorFeed(identity.email, displayCurrency);
    return NextResponse.json(feed);
  } catch (err) {
    console.error("monitor feed GET failed", err);
    return NextResponse.json({ error: "failed to load monitor feed" }, { status: 500 });
  }
}
