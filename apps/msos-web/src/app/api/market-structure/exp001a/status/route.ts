import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function engineConfig(): { url: string; token: string } | null {
  const configured = process.env.MARKET_STRUCTURE_ENGINE_URL?.trim();
  const token = process.env.MARKET_STRUCTURE_ENGINE_TOKEN?.trim();
  if (!configured || !token) return null;
  return { url: configured, token };
}

function resolveEngineUrl(configured: string, enginePath: string): string {
  const base = new URL(configured.includes("://") ? configured : `https://${configured}`);
  const desired = new URL(enginePath, "https://engine.local");

  if (base.pathname === "/status") {
    base.search = "";
    base.searchParams.set("engine_path", `${desired.pathname}${desired.search}`);
    return base.toString();
  }

  base.pathname = desired.pathname;
  base.search = desired.search;
  return base.toString();
}

export async function GET() {
  const config = engineConfig();
  if (!config) {
    return NextResponse.json(
      { status: "UNAVAILABLE", detail: "Market-structure engine is not configured." },
      { status: 503 },
    );
  }

  try {
    const response = await fetch(resolveEngineUrl(config.url, "/v1/research/exp001a/status"), {
      headers: {
        Authorization: `Bearer ${config.token}`,
        Accept: "application/json",
      },
      cache: "no-store",
      signal: AbortSignal.timeout(15_000),
    });
    const body = await response.json().catch(() => ({ status: "ERROR", detail: "Engine returned invalid JSON." }));
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json(
      { status: "UNAVAILABLE", detail: "Could not reach EXP-001A runtime status." },
      { status: 503 },
    );
  }
}
