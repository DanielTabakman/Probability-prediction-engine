import { Suspense } from "react";

import { StrategyLabClientShell } from "@/components/StrategyLabClientShell";
import type { DisplayPayload } from "@/lib/ppeDisplayPayload";
import { LAB_ASSET_QUERY_PARAM } from "@/lib/ppeDisplayPayload";

type StrategyLabContentProps = {
  displayPayload?: DisplayPayload | null;
};

const DISTRIBUTION_EXPORT_API_PATH = "/api/ppe-display-api/distribution-export";

function resolveCatalogAssetId(displayPayload: DisplayPayload | null): string {
  const raw = displayPayload?.asset?.id?.trim().toUpperCase();
  return raw || "BTC";
}

function buildDistributionExportHref(assetId: string): string {
  return `${DISTRIBUTION_EXPORT_API_PATH}?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(assetId)}`;
}

export function StrategyLabContent({ displayPayload = null }: StrategyLabContentProps) {
  const assetId = resolveCatalogAssetId(displayPayload);
  const live = displayPayload != null;
  const downloadHref = buildDistributionExportHref(assetId);

  return (
    <>
      <div className="lab-export-toolbar" data-tour="lab-distribution-export">
        {live ? (
          <a href={downloadHref} className="btn slim dark" download>
            Download distribution stats (CSV)
          </a>
        ) : (
          <span
            className="btn slim dark"
            aria-disabled="true"
            title="Live data required for distribution export"
          >
            Download distribution stats (CSV)
          </span>
        )}
        <p className="footer-note lab-export-note">
          {live
            ? "Research export — same schema as implied lab. Simulation and paper workflows only; not investment advice."
            : "Sample mode — live data loads automatically when available; export unlocks with live chain data."}
        </p>
      </div>

      <Suspense fallback={<p className="footer-note">Loading Strategy Lab…</p>}>
        <StrategyLabClientShell initialPayload={displayPayload} />
      </Suspense>
    </>
  );
}
