import Link from "next/link";
import type { ReactNode } from "react";

import { LAB_ASSET_QUERY_PARAM } from "@/lib/ppeDisplayPayload";
import { MSOS_ROUTES } from "@/lib/msosPublicUrls";

/** Default asset when a module has no live catalog context (Command Center home). */
export const DEFAULT_CROSS_MODULE_ASSET = "BTC";

/** Strategy Lab tour anchor — hook for horizon region thesis onboarding. */
export const HORIZON_REGION_TOUR_ANCHOR = "lab-horizon-nav";

export const HORIZON_REGION_TOUR_COPY =
  "Chart a price × time region on Options Horizon — drag a box, read implied mass, then return here to express the thesis.";

export function normalizeNavAssetId(raw: string | null | undefined): string {
  const normalized = raw?.trim().toUpperCase();
  return normalized || DEFAULT_CROSS_MODULE_ASSET;
}

export function buildOptionsHorizonPath(assetId: string): string {
  const normalized = normalizeNavAssetId(assetId);
  return `${MSOS_ROUTES.optionsHorizon}?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(normalized)}`;
}

export const LAB_EXPIRY_QUERY_PARAM = "expiry";

export function buildStrategyLabPathWithAsset(assetId: string): string {
  const normalized = normalizeNavAssetId(assetId);
  return `${MSOS_ROUTES.strategyLab}?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(normalized)}`;
}

export function buildStrategyLabPathWithAssetAndExpiry(
  assetId: string,
  expiryDate: string,
): string {
  const normalized = normalizeNavAssetId(assetId);
  const params = new URLSearchParams({
    [LAB_ASSET_QUERY_PARAM]: normalized,
    [LAB_EXPIRY_QUERY_PARAM]: expiryDate,
  });
  return `${MSOS_ROUTES.strategyLab}?${params.toString()}`;
}

export function assetAwareModuleHref(moduleHref: string, assetId: string): string {
  if (moduleHref === MSOS_ROUTES.optionsHorizon) {
    return buildOptionsHorizonPath(assetId);
  }
  if (moduleHref === MSOS_ROUTES.strategyLab) {
    return buildStrategyLabPathWithAsset(assetId);
  }
  return moduleHref;
}

type HorizonNavLinkProps = {
  assetId: string;
  className?: string;
  children: ReactNode;
  dataTour?: string;
};

export function HorizonNavLink({ assetId, className, children, dataTour }: HorizonNavLinkProps) {
  return (
    <Link href={buildOptionsHorizonPath(assetId)} className={className} data-tour={dataTour}>
      {children}
    </Link>
  );
}
