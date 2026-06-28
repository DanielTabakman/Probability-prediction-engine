"use client";

import { useEffect, useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { LAB_ASSET_QUERY_PARAM, type LabAssetId } from "@/lib/ppeDisplayPayload";
import { resolveLabAssetId, saveStoredLabAssetId } from "@/lib/strategyLabAsset";

export type UseResolvedLabAssetIdOptions = {
  thesisAssetId?: string | null;
  allowedIds?: readonly string[];
  catalogDefault?: string | null;
  /** When false, do not rewrite bare URLs (e.g. Strategy Lab compare uses picker navigation). */
  syncUrl?: boolean;
};

export function useResolvedLabAssetId(options: UseResolvedLabAssetIdOptions = {}): LabAssetId {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const query = searchParams.get(LAB_ASSET_QUERY_PARAM);

  const assetId = useMemo(
    () =>
      resolveLabAssetId({
        query,
        thesisAssetId: options.thesisAssetId,
        allowedIds: options.allowedIds,
        catalogDefault: options.catalogDefault,
        useStored: true,
      }),
    [query, options.thesisAssetId, options.allowedIds, options.catalogDefault],
  );

  useEffect(() => {
    saveStoredLabAssetId(assetId);
  }, [assetId]);

  useEffect(() => {
    if (options.syncUrl === false) {
      return;
    }
    if (query?.trim()) {
      return;
    }
    const params = new URLSearchParams(searchParams.toString());
    params.set(LAB_ASSET_QUERY_PARAM, assetId);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }, [assetId, query, pathname, router, searchParams, options.syncUrl]);

  return assetId;
}
