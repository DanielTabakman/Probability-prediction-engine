import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ExposureMenuClient } from "@/components/ExposureMenuClient";
import { fetchAssetCatalogServer } from "@/lib/ppeAssetCatalog";
import {
  DEFAULT_EXPOSURE_DIRECTION,
  DEFAULT_EXPOSURE_HORIZON,
  fetchExposureMenu,
  normalizeExposureAssetId,
  normalizeExposureDirection,
  normalizeExposureHorizon,
} from "@/lib/ppeExposureMenu";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Exposure menu | Market Structure OS",
  description:
    "Compare paths to asset exposure — spot, options, and planned rails. Simulation only; not trade recommendations.",
};

type ExposurePageProps = {
  searchParams: Promise<{
    asset?: string | string[];
    direction?: string | string[];
    horizon?: string | string[];
  }>;
};

function firstParam(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function ExposurePage({ searchParams }: ExposurePageProps) {
  const params = await searchParams;
  const catalog = await fetchAssetCatalogServer();
  const assetId = normalizeExposureAssetId(firstParam(params.asset), catalog);
  const direction = normalizeExposureDirection(
    firstParam(params.direction),
    DEFAULT_EXPOSURE_DIRECTION,
  );
  const horizon = normalizeExposureHorizon(firstParam(params.horizon), DEFAULT_EXPOSURE_HORIZON);

  const initialPayload = await fetchExposureMenu(assetId, direction, horizon);

  return (
    <AppShell activeNavId="exposure">
      <ExposureMenuClient
        initialPayload={initialPayload}
        initialAsset={assetId}
        initialDirection={direction}
        initialHorizon={horizon}
      />
    </AppShell>
  );
}
