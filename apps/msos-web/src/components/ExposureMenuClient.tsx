"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ExposurePathCard } from "@/components/ExposurePathCard";
import { demoExposureMenuForAsset } from "@/data/exposureMenuFixtures";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import {
  buildExposurePagePath,
  DEFAULT_EXPOSURE_ASSET_ID,
  DEFAULT_EXPOSURE_DIRECTION,
  DEFAULT_EXPOSURE_HORIZON,
  EXPOSURE_PROOF_ASSETS,
  fetchExposureMenuClient,
  normalizeExposureAssetId,
  normalizeExposureDirection,
  normalizeExposureHorizon,
  type ExposureDirection,
  type ExposureMenuPayload,
  type HorizonChip,
} from "@/lib/ppeExposureMenu";

type ExposureMenuClientProps = {
  initialPayload: ExposureMenuPayload | null;
  initialAsset?: string;
  initialDirection?: string;
  initialHorizon?: string;
};

const DIRECTION_OPTIONS: { id: ExposureDirection; label: string }[] = [
  { id: "long", label: "Long" },
  { id: "short", label: "Short" },
  { id: "neutral", label: "Neutral" },
];

const HORIZON_OPTIONS: { id: HorizonChip; label: string }[] = [
  { id: "any", label: "Any" },
  { id: "3m", label: "3m" },
  { id: "12m", label: "12m" },
];

export function ExposureMenuClient({
  initialPayload,
  initialAsset,
  initialDirection,
  initialHorizon,
}: ExposureMenuClientProps) {
  const router = useRouter();
  const assetId = normalizeExposureAssetId(initialAsset, DEFAULT_EXPOSURE_ASSET_ID);
  const direction = normalizeExposureDirection(initialDirection, DEFAULT_EXPOSURE_DIRECTION);
  const horizon = normalizeExposureHorizon(initialHorizon, DEFAULT_EXPOSURE_HORIZON);

  const [payload, setPayload] = useState<ExposureMenuPayload | null>(initialPayload);
  const [loading, setLoading] = useState(!initialPayload);
  const [live, setLive] = useState(Boolean(initialPayload));

  const refresh = useCallback(async () => {
    setLoading(true);
    const data = await fetchExposureMenuClient(assetId, direction, horizon);
    if (data) {
      setPayload(data);
      setLive(true);
    } else {
      setPayload(demoExposureMenuForAsset(assetId, direction, horizon));
      setLive(false);
    }
    setLoading(false);
  }, [assetId, direction, horizon]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const onAssetChange = (nextAsset: string) => {
    const normalized = normalizeExposureAssetId(nextAsset);
    router.replace(buildExposurePagePath(normalized, direction, horizon));
  };

  const onDirectionChange = (nextDirection: ExposureDirection) => {
    router.replace(buildExposurePagePath(assetId, nextDirection, horizon));
  };

  const onHorizonChange = (nextHorizon: HorizonChip) => {
    router.replace(buildExposurePagePath(assetId, direction, nextHorizon));
  };

  const paths = payload?.paths ?? [];
  const footerCopy = payload?.footer_copy ?? "";
  const spotUsd = payload?.spot_usd;

  const statusNote = useMemo(() => {
    if (loading) return "Loading paths from the display API…";
    if (!live) {
      return "Sample paths — connect the display API for live spot and options quotes.";
    }
    if (payload?.status === "insufficient_chain") {
      return "Thin or missing options chain — spot may still show; check trust badges.";
    }
    return null;
  }, [loading, live, payload?.status]);

  return (
    <div className="exposure-menu-work">
      <header className="page-header">
        <div>
          <p className="eyebrow">Exposure menu</p>
          <h1>Paths to {assetId} exposure</h1>
          <p className="panel-sub">
            Ranked ways to get exposure — for comparison only, not trade recommendations.
            Simulation and research support.
          </p>
        </div>
      </header>

      <section className="exposure-menu-intake panel compact" aria-label="Exposure intake">
        <label className="exposure-menu-field">
          <span>Asset</span>
          <select value={assetId} onChange={(event) => onAssetChange(event.target.value)}>
            {EXPOSURE_PROOF_ASSETS.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </label>

        <div className="exposure-menu-chip-group" role="group" aria-label="Direction">
          <span className="micro">Direction</span>
          <div className="belief-preset-grid">
            {DIRECTION_OPTIONS.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`belief-preset${direction === option.id ? " active" : ""}`}
                aria-pressed={direction === option.id}
                onClick={() => onDirectionChange(option.id)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="exposure-menu-chip-group" role="group" aria-label="Horizon">
          <span className="micro">Horizon</span>
          <div className="belief-preset-grid">
            {HORIZON_OPTIONS.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`belief-preset${horizon === option.id ? " active" : ""}`}
                aria-pressed={horizon === option.id}
                onClick={() => onHorizonChange(option.id)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {typeof spotUsd === "number" && Number.isFinite(spotUsd) ? (
          <p className="exposure-menu-spot panel-sub">
            Spot reference: <strong>${spotUsd.toLocaleString("en-US")}</strong>
            {live ? <span className="tag teal">Live</span> : <span className="tag amber">Sample</span>}
          </p>
        ) : null}

        {statusNote ? (
          <p className="exposure-menu-status panel-sub" role="status">
            {statusNote}
          </p>
        ) : null}
      </section>

      <section className="exposure-path-grid" aria-label="Exposure path cards" aria-busy={loading}>
        {paths.map((path) => (
          <ExposurePathCard key={path.path_id} path={path} />
        ))}
      </section>

      <footer className="exposure-menu-footer panel-sub">
        <p>{footerCopy}</p>
        <p>{DEMO_FOOTER}</p>
      </footer>
    </div>
  );
}
