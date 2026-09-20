import { NextRequest, NextResponse } from "next/server";

export function GET(request: NextRequest) {
  const environment = request.nextUrl.hostname.startsWith("staging.")
    ? "staging"
    : "production";
  const help = {
    name: "Options Market Read",
    environment,
    purpose: "Explain what BTC options are pricing for a target date. Informational only.",
    method: "GET",
    endpoint: "/v1/options-market-read",
    human_interface: "/options-market-read",
    parameters: {
      asset: {
        required: false,
        default: "BTC",
        supported_values: ["BTC"],
      },
      target_date: {
        required: false,
        format: "YYYY-MM-DD",
        default: "snapshot as_of date plus 30 calendar days",
      },
    },
    examples: [
      "/v1/options-market-read",
      "/v1/options-market-read?asset=BTC&target_date=2026-12-25",
    ],
    response_guide: {
      answer: "The plain-English market read. Show this first to a person.",
      metrics: "Spot, implied forward, median, middle-50% range, and ATM implied volatility.",
      interpretation: "Expiry timing, range versus spot, and adjacent-expiry uncertainty context.",
      disclosures: "Methodology, source, freshness, and limitations. Suitable for expandable small print.",
      resolved_expiry: "The listed contract actually analyzed.",
      as_of: "UTC time when the cached market snapshot was built.",
    },
    date_resolution: {
      rule: "Exact expiry if available; otherwise nearest live expiry, with ties going to the later expiry.",
      maximum_gap_days: 14,
      disclosure_fields: [
        "effective_target_date",
        "resolved_expiry",
        "expiry_offset_days",
        "expiry_resolution",
      ],
    },
    guarantees: [
      "Deterministic output for the same snapshot and request.",
      "BTC only in this version.",
      "No trade recommendation, opportunity ranking, execution, or forecast.",
    ],
  } as const;

  return NextResponse.json(help, {
    headers: {
      "Cache-Control": "public, max-age=300",
    },
  });
}
