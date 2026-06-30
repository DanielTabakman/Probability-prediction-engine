import { NextRequest, NextResponse } from "next/server";

import {
  buildDistributionExportUpstreamUrl,
  LAB_ASSET_QUERY_PARAM,
  normalizeAssetId,
} from "@/lib/distributionExportUpstream";

export const runtime = "nodejs";

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
