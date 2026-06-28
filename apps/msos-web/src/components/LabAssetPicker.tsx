"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import {
  FALLBACK_ASSET_PICKER,
  assetBucketForId,
  bucketsFromCatalog,
  fetchAssetCatalog,
  findCatalogAsset,
  trustNotesForAsset,
  type AssetPickerBuckets,
  type CatalogAsset,
} from "@/lib/ppeAssetCatalog";

type LabAssetPickerProps = {
  selectedAssetId: string;
  buildAssetHref: (assetId: string) => string;
  className?: string;
};

type AssetCategorySelectProps = {
  label: string;
  assets: CatalogAsset[];
  value: string;
  active: boolean;
  placeholder: string;
  onSelect: (assetId: string) => void;
};

function AssetCategorySelect({
  label,
  assets,
  value,
  active,
  placeholder,
  onSelect,
}: AssetCategorySelectProps) {
  const canPick = assets.length > 0;
  const singleAssetId = assets.length === 1 ? assets[0].id : null;
  // Only lock the control when this bucket is active and has no alternate within it.
  const disabled = !canPick || (active && assets.length <= 1);
  const switchTarget = !active && singleAssetId ? singleAssetId : null;

  return (
    <div
      className={`lab-asset-field${active ? " active" : ""}${switchTarget ? " switchable" : ""}`}
      onClick={
        switchTarget
          ? () => {
              onSelect(switchTarget);
            }
          : undefined
      }
      onKeyDown={
        switchTarget
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelect(switchTarget);
              }
            }
          : undefined
      }
      role={switchTarget ? "button" : undefined}
      tabIndex={switchTarget ? 0 : undefined}
    >
      <span className="lab-asset-k">{label}</span>
      <label className="lab-asset-select">
        <select
          value={value}
          disabled={disabled}
          onClick={(event) => {
            if (switchTarget) {
              event.stopPropagation();
            }
          }}
          onChange={(event) => {
            const next = event.target.value;
            if (next) {
              onSelect(next);
            }
          }}
          aria-label={`${label} options asset`}
        >
          {!value ? (
            <option value="" disabled>
              {placeholder}
            </option>
          ) : null}
          {assets.map((asset) => (
            <option key={asset.id} value={asset.id}>
              {asset.id}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

/** Crypto + stocks dropdowns — reads PPE catalog.json (display only). */
export function LabAssetPicker({
  selectedAssetId,
  buildAssetHref,
  className,
}: LabAssetPickerProps) {
  const router = useRouter();
  const [buckets, setBuckets] = useState<AssetPickerBuckets>(FALLBACK_ASSET_PICKER);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const catalog = await fetchAssetCatalog();
      if (cancelled || !catalog) {
        return;
      }
      setBuckets(bucketsFromCatalog(catalog));
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const activeBucket = assetBucketForId(selectedAssetId, buckets);
  const cryptoValue = activeBucket === "crypto" ? selectedAssetId : "";
  const stocksValue = activeBucket === "stocks" ? selectedAssetId : "";
  const trustNotes = useMemo(
    () => trustNotesForAsset(findCatalogAsset(buckets, selectedAssetId)),
    [buckets, selectedAssetId],
  );

  function navigate(assetId: string) {
    router.push(buildAssetHref(assetId));
  }

  return (
    <div
      className={`lab-asset-picker${className ? ` ${className}` : ""}`.trim()}
      data-tour="lab-asset"
    >
      <AssetCategorySelect
        label="Crypto"
        assets={buckets.crypto}
        value={cryptoValue}
        active={activeBucket === "crypto"}
        placeholder="Pick crypto"
        onSelect={navigate}
      />
      <AssetCategorySelect
        label="Stocks"
        assets={buckets.stocks}
        value={stocksValue}
        active={activeBucket === "stocks"}
        placeholder="Pick stocks"
        onSelect={navigate}
      />
      {trustNotes.length > 0 ? (
        <ul className="lab-trust-notes" aria-label={`Trust notes for ${selectedAssetId}`}>
          {trustNotes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
