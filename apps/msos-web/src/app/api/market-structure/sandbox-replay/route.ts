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

export async function POST(request: Request) {
  const config = engineConfig();
  if (!config) {
    return NextResponse.json(
      { status: "UNAVAILABLE", detail: "Market-structure engine is not configured." },
      { status: 503 },
    );
  }

  try {
    const body = await request.json();
    const response = await fetch(resolveEngineUrl(config.url, "/v1/research/sandbox-replay"), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.token}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(120_000),
    });
    const payload = await response.json().catch(() => ({
      status: "ERROR",
      detail: "Engine returned invalid JSON.",
    }));
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Could not run raw sandbox replay.";
    return NextResponse.json({ status: "UNAVAILABLE", detail }, { status: 503 });
  }
}
