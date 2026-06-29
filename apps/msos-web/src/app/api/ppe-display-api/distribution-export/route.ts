import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

const LAB_ASSET_QUERY_PARAM = "asset";

const PUBLIC_DISTRIBUTION_EXPORT_PATH =
  process.env.NEXT_PUBLIC_PPE_DISTRIBUTION_EXPORT_API_URL?.trim() ??
  "/ppe-display-api/distribution-export.csv";

function normalizeAssetId(raw: string | null): string {
  const trimmed = (raw ?? "BTC").trim().toUpperCase();
  return trimmed || "BTC";
}

/** Server-side upstream (Docker internal) or same-origin public path via Caddy. */
export function buildDistributionExportUpstreamUrl(assetId: string): string {
  const asset = normalizeAssetId(assetId);
  const serverUrl = process.env.PPE_DISPLAY_API_SERVER_URL?.trim();
  if (serverUrl) {
    const base = serverUrl.replace(/\/display\.json(\?.*)?$/i, "");
    return `${base}/distribution-export.csv?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(asset)}`;
  }
  const separator = PUBLIC_DISTRIBUTION_EXPORT_PATH.includes("?") ? "&" : "?";
  return `${PUBLIC_DISTRIBUTION_EXPORT_PATH}${separator}${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(asset)}`;
}

export async function GET(request: NextRequest) {
  const asset = normalizeAssetId(request.nextUrl.searchParams.get(LAB_ASSET_QUERY_PARAM));
  const upstream = buildDistributionExportUpstreamUrl(asset);

  try {
    const isAbsolute = upstream.startsWith("http://") || upstream.startsWith("https://");
    const fetchUrl = isAbsolute ? upstream : new URL(upstream, request.url).toString();
    const upstreamResponse = await fetch(fetchUrl, { cache: "no-store" });
    if (!upstreamResponse.ok) {
      return NextResponse.json(
        {
          kind: "distribution_export_error",
          error: `upstream returned ${upstreamResponse.status}`,
        },
        { status: upstreamResponse.status >= 500 ? upstreamResponse.status : 503 },
      );
    }
    const csv = await upstreamResponse.text();
    const slug = asset.toLowerCase();
    return new NextResponse(csv, {
      status: 200,
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename="ppe_${slug}_distribution_stats.csv"`,
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return NextResponse.json(
      { kind: "distribution_export_error", error: "distribution export fetch failed" },
      { status: 503 },
    );
  }
}
