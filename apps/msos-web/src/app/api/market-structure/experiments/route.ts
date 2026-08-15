import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const DEFAULT_SOURCE = "ndax";
const DEFAULT_FORWARD_SECONDS = 14_400;

function engineConfig(): { url: string; token: string } | null {
  const configured = process.env.MARKET_STRUCTURE_ENGINE_URL?.trim();
  const token = process.env.MARKET_STRUCTURE_ENGINE_TOKEN?.trim();
  if (!configured || !token) return null;
  return { url: configured, token };
}

function resolveEngineUrl(configured: string, enginePath: string): string {
  const base = new URL(configured.includes("://") ? configured : `https://${configured}`);
  const desired = new URL(enginePath, "https://engine.local");

  // Current Condor Cloudflare compatibility route exposes exact /status only.
  // The edge router accepts an authenticated engine_path query for v0 research APIs.
  if (base.pathname === "/status") {
    base.search = "";
    base.searchParams.set("engine_path", `${desired.pathname}${desired.search}`);
    return base.toString();
  }

  base.pathname = desired.pathname;
  base.search = desired.search;
  return base.toString();
}

async function engineFetch(enginePath: string, init?: RequestInit): Promise<Response> {
  const config = engineConfig();
  if (!config) {
    throw new Error("NOT_CONFIGURED");
  }
  return fetch(resolveEngineUrl(config.url, enginePath), {
    ...init,
    headers: {
      Authorization: `Bearer ${config.token}`,
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
    signal: AbortSignal.timeout(60_000),
  });
}

async function passThrough(response: Response): Promise<NextResponse> {
  const body = await response.json().catch(() => ({ status: "ERROR", detail: "Engine returned invalid JSON." }));
  return NextResponse.json(body, { status: response.status });
}

export async function GET() {
  try {
    return passThrough(await engineFetch("/v1/experiments?limit=12"));
  } catch (error) {
    const detail = error instanceof Error && error.message === "NOT_CONFIGURED"
      ? "Market-structure engine is not configured."
      : "Could not reach the market-structure research API.";
    return NextResponse.json({ status: "UNAVAILABLE", detail, results: [] }, { status: 503 });
  }
}

export async function POST() {
  try {
    return passThrough(await engineFetch("/v1/experiments/forward-validation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: DEFAULT_SOURCE,
        forward_seconds: DEFAULT_FORWARD_SECONDS,
      }),
    }));
  } catch (error) {
    const detail = error instanceof Error && error.message === "NOT_CONFIGURED"
      ? "Market-structure engine is not configured."
      : "Could not run the market-structure experiment.";
    return NextResponse.json({ status: "UNAVAILABLE", detail }, { status: 503 });
  }
}
