import Link from "next/link";

import { buildStrategyLabPath, DEFAULT_LAB_ASSET_ID } from "@/lib/ppeDisplayPayload";

type MonitorEmptyStateProps = {
  assetTicker?: string;
};

export function MonitorEmptyState({ assetTicker }: MonitorEmptyStateProps) {
  const ticker = assetTicker?.trim();
  const spotPhrase = ticker ? `live ${ticker}` : "live spot";
  const labHref = buildStrategyLabPath(
    ticker && ticker.toUpperCase() !== DEFAULT_LAB_ASSET_ID ? ticker : DEFAULT_LAB_ASSET_ID,
  );

  return (
    <div className="monitor-empty-state" role="status">
      <strong>No paper trades yet</strong>
      <p>
        Save a sketch in Strategy Lab after you confirm your view — we&apos;ll show {spotPhrase}{" "}
        versus your saved prices here. No broker connection required.
      </p>
      <Link href={labHref} className="btn slim primary">
        Open Strategy Lab
      </Link>
    </div>
  );
}
