"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ExposureCompareDrawer } from "@/components/ExposureCompareDrawer";
import { LabAssetPicker } from "@/components/LabAssetPicker";
import { ExposurePathCard } from "@/components/ExposurePathCard";
import { demoExposureMenuForAsset } from "@/data/exposureMenuFixtures";
import { assetBucketForId, bucketsFromCatalog, fetchAssetCatalog } from "@/lib/ppeAssetCatalog";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import {
  buildExposurePagePath,
  DEFAULT_EXPOSURE_DIRECTION,
  DEFAULT_EXPOSURE_HORIZON,
  fetchExposureMenuClient,
  fitLensOptionsForDirection,
  normalizeExposureDirection,
  normalizeExposureHorizon,
  pathMatchesFitLens,
  resolveExposureSections,
  type ExposureDirection,
  type ExposureMenuPayload,
  type ExposurePathRecord,
  type FitLensId,
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

const HORIZON_HINTS: Partial<Record<HorizonChip, string>> = {
  "3m": "Options expiries filtered to roughly 3–6 month window.",
  "12m": "Options expiries filtered toward LEAPS / 12m+ horizon.",
};

export function ExposureMenuClient({
  initialPayload,
  initialAsset,
  initialDirection,
  initialHorizon,
}: ExposureMenuClientProps) {
  const router = useRouter();
  const assetId = (initialAsset ?? "").trim().toUpperCase();
  const direction = normalizeExposureDirection(initialDirection, DEFAULT_EXPOSURE_DIRECTION);
  const horizon = normalizeExposureHorizon(initialHorizon, DEFAULT_EXPOSURE_HORIZON);

  const [payload, setPayload] = useState<ExposureMenuPayload | null>(initialPayload);
  const [loading, setLoading] = useState(!initialPayload);
  const [live, setLive] = useState(Boolean(initialPayload));
  const [assetBucket, setAssetBucket] = useState<"crypto" | "stocks" | null>(null);
  const [activeFitLens, setActiveFitLens] = useState<FitLensId | null>(null);
  const [pinnedIds, setPinnedIds] = useState<string[]>([]);
  const [compareOpen, setCompareOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const catalog = await fetchAssetCatalog();
      if (cancelled || !catalog) {
        return;
      }
      const buckets = bucketsFromCatalog(catalog);
      setAssetBucket(assetBucketForId(assetId, buckets));
    })();
    return () => {
      cancelled = true;
    };
  }, [assetId]);

  const refresh = useCallback(async () => {
    setLoading(true);
    const data = await fetchExposureMenuClient(assetId, direction, horizon);
    if (data) {
      setPayload(data);
      setLive(true);
    } else {
      setPayload(demoExposureMenuForAsset(assetId, direction, horizon, assetBucket));
      setLive(false);
    }
    setLoading(false);
  }, [assetId, assetBucket, direction, horizon]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    setPinnedIds([]);
    setCompareOpen(false);
  }, [assetId, direction, horizon]);

  const buildAssetHref = useCallback(
    (nextAsset: string) => buildExposurePagePath(nextAsset, direction, horizon),
    [direction, horizon],
  );

  const onDirectionChange = (nextDirection: ExposureDirection) => {
    setActiveFitLens(null);
    router.replace(buildExposurePagePath(assetId, nextDirection, horizon));
  };

  const onHorizonChange = (nextHorizon: HorizonChip) => {
    router.replace(buildExposurePagePath(assetId, direction, nextHorizon));
  };

  const paths = payload?.paths ?? [];
  const pathById = useMemo(() => {
    const map = new Map<string, ExposurePathRecord>();
    for (const path of paths) {
      map.set(path.path_id, path);
    }
    return map;
  }, [paths]);

  const sections = useMemo(
    () => (payload ? resolveExposureSections(payload) : []),
    [payload],
  );

  const footerCopy = payload?.footer_copy ?? "";
  const spotUsd = payload?.spot_usd;
  const liveCount = payload?.live_path_count ?? 0;
  const plannedCount = payload?.planned_path_count ?? paths.filter((p) => p.trust_badge === "Planned").length;

  const fitLensOptions = fitLensOptionsForDirection(direction);

  const pinnedPaths = useMemo(
    () =>
      pinnedIds
        .map((id) => pathById.get(id))
        .filter((path): path is ExposurePathRecord => Boolean(path))
        .slice(0, 2),
    [pathById, pinnedIds],
  );

  const togglePin = (pathId: string) => {
    setPinnedIds((current) => {
      if (current.includes(pathId)) {
        return current.filter((id) => id !== pathId);
      }
      if (current.length >= 2) {
        return [current[1]!, pathId];
      }
      return [...current, pathId];
    });
  };

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

  const horizonHint = HORIZON_HINTS[horizon];

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
          {!loading && paths.length > 0 ? (
            <p className="exposure-menu-counts panel-sub">
              {liveCount} live
              {plannedCount > 0 ? ` · ${plannedCount} planned` : ""}
            </p>
          ) : null}
        </div>
      </header>

      <section className="exposure-menu-intake panel compact" aria-label="Exposure intake">
        <LabAssetPicker
          selectedAssetId={assetId}
          buildAssetHref={buildAssetHref}
          className="exposure-menu-asset-picker"
        />

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

        {horizonHint ? <p className="exposure-menu-status panel-sub">{horizonHint}</p> : null}

        {statusNote ? (
          <p className="exposure-menu-status panel-sub" role="status">
            {statusNote}
          </p>
        ) : null}
      </section>

      <section className="exposure-menu-fit panel compact" aria-label="Fit priorities">
        <div>
          <span className="micro">What matters most?</span>
          <p className="panel-sub exposure-menu-fit-intro">
            Highlights paths that align with a priority — fit is not a recommendation.
          </p>
        </div>
        <div className="belief-preset-grid">
          {fitLensOptions.map((option) => (
            <button
              key={option.id}
              type="button"
              className={`belief-preset${activeFitLens === option.id ? " active" : ""}`}
              aria-pressed={activeFitLens === option.id}
              onClick={() =>
                setActiveFitLens((current) => (current === option.id ? null : option.id))
              }
            >
              {option.label}
            </button>
          ))}
          {activeFitLens ? (
            <button
              type="button"
              className="belief-preset"
              onClick={() => setActiveFitLens(null)}
            >
              Clear
            </button>
          ) : null}
        </div>
      </section>

      {!loading && paths.length === 0 ? (
        <section className="exposure-menu-empty panel" role="status">
          <p>No exposure paths for this asset and direction yet.</p>
          <p className="panel-sub">
            {direction === "neutral"
              ? "Neutral / hedged structures are not cataloged in v1 — try Long or Short, or open Strategy Lab for belief-based structures."
              : "Try Long or Short, or pick another asset from the registry."}
          </p>
        </section>
      ) : null}

      {sections.map((section) => {
        const sectionPaths = section.path_ids
          .map((id) => pathById.get(id))
          .filter((path): path is ExposurePathRecord => Boolean(path));
        if (!sectionPaths.length) {
          return null;
        }
        return (
          <section
            key={section.section_key}
            className="exposure-menu-section"
            aria-label={section.title}
            aria-busy={loading}
          >
            <header className="exposure-menu-section-head">
              <h2>{section.title}</h2>
              {section.subcopy ? <p className="panel-sub">{section.subcopy}</p> : null}
            </header>
            <div className="exposure-path-grid">
              {sectionPaths.map((path) => {
                const matches = pathMatchesFitLens(path, activeFitLens);
                return (
                  <ExposurePathCard
                    key={path.path_id}
                    assetId={assetId}
                    path={path}
                    activeFitLens={activeFitLens}
                    dimmed={Boolean(activeFitLens && !matches)}
                    pinned={pinnedIds.includes(path.path_id)}
                    pinDisabled={!pinnedIds.includes(path.path_id) && pinnedIds.length >= 2}
                    onPinToggle={() => togglePin(path.path_id)}
                  />
                );
              })}
            </div>
          </section>
        );
      })}

      {pinnedIds.length === 1 ? (
        <p className="exposure-pin-hint panel-sub" role="status">
          Pin one more path to compare side by side.
        </p>
      ) : null}

      {pinnedPaths.length === 2 ? (
        <div className="exposure-compare-bar panel">
          <p>
            Compare: <strong>{pinnedPaths[0]!.label}</strong> vs{" "}
            <strong>{pinnedPaths[1]!.label}</strong>
          </p>
          <div className="exposure-compare-bar-actions">
            <button type="button" className="btn slim" onClick={() => setCompareOpen(true)}>
              Open compare
            </button>
            <button type="button" className="btn slim ghost" onClick={() => setPinnedIds([])}>
              Clear pins
            </button>
          </div>
        </div>
      ) : null}

      {pinnedPaths.length === 2 ? (
        <ExposureCompareDrawer
          paths={[pinnedPaths[0]!, pinnedPaths[1]!]}
          footerCopy={footerCopy}
          open={compareOpen}
          onClose={() => setCompareOpen(false)}
        />
      ) : null}

      <footer className="exposure-menu-footer panel-sub">
        <p>{footerCopy}</p>
        <p>{DEMO_FOOTER}</p>
      </footer>
    </div>
  );
}
