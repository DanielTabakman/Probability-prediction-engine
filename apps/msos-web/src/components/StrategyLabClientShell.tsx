"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { LabAssetPicker } from "@/components/LabAssetPicker";
import { StrategyLabWorkSection } from "@/components/StrategyLabWorkSection";
import { PlatformTutorial } from "@/components/PlatformTutorial";
import { PendingPaperTradeBanner } from "@/components/PendingPaperTradeBanner";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import {
  LAB_ASSET_QUERY_PARAM,
  fetchDisplayPayloadClient,
  isPayloadForSelectedAsset,
  resolveDisplayAssetMeta,
  type DisplayPayload,
  type LabAssetId,
} from "@/lib/ppeDisplayPayload";
import {
  FALLBACK_ASSET_PICKER,
  bucketsFromCatalog,
  fetchAssetCatalog,
  listSelectableAssetIds,
} from "@/lib/ppeAssetCatalog";
import { resolveLabAssetId, saveStoredLabAssetId } from "@/lib/strategyLabAsset";
import { buildWorkflowStepHref } from "@/lib/strategyLabWorkflow";
import {
  LAB_DATA_DEMO_PILL,
  LAB_DATA_LOADING_PILL,
  LAB_DEMO_BANNER_TITLE,
  labDataLivePill,
  labDemoBannerBody,
  labLoadingBannerBody,
  type LabDataMode,
} from "@/lib/strategyLabCopy";
import {
  hasTutorialSearchParams,
  isPlatformTutorialComplete,
  resolveTutorialBeginnerMode,
  resolveTutorialSteps,
  stripTutorialSearchParams,
} from "@/lib/platformTutorial";

type StrategyLabClientShellProps = {
  initialPayload: DisplayPayload | null;
};

function resolveInitialMode(
  initialPayload: DisplayPayload | null,
  assetId: LabAssetId,
): LabDataMode {
  if (initialPayload && isPayloadForSelectedAsset(initialPayload, assetId)) {
    return "live";
  }
  return "loading";
}

function buildAssetHref(
  pathname: string,
  searchParams: URLSearchParams,
  assetId: LabAssetId,
): string {
  const params = new URLSearchParams(searchParams.toString());
  params.set(LAB_ASSET_QUERY_PARAM, assetId.trim().toUpperCase());
  const qs = params.toString();
  return qs ? `${pathname}?${qs}` : pathname;
}

export function StrategyLabClientShell({ initialPayload }: StrategyLabClientShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [catalogAssetIds, setCatalogAssetIds] = useState<string[]>(() =>
    listSelectableAssetIds(FALLBACK_ASSET_PICKER),
  );
  const [catalogDefault, setCatalogDefault] = useState<string | null>(null);
  const queryAsset = searchParams.get(LAB_ASSET_QUERY_PARAM);
  const selectedAssetId = useMemo(
    () =>
      resolveLabAssetId({
        query: queryAsset,
        allowedIds: catalogAssetIds,
        catalogDefault,
        useStored: true,
      }),
    [queryAsset, catalogAssetIds, catalogDefault],
  );
  const [payload, setPayload] = useState<DisplayPayload | null>(initialPayload);
  const [mode, setMode] = useState<LabDataMode>(() =>
    resolveInitialMode(initialPayload, selectedAssetId),
  );
  const [tutorialOpen, setTutorialOpen] = useState(false);
  const [tutorialBeginner, setTutorialBeginner] = useState(false);
  const assetMeta = useMemo(
    () => resolveDisplayAssetMeta(payload, selectedAssetId),
    [payload, selectedAssetId],
  );
  const trustState = payload?.trust_state ?? payload?.meta?.trust_state;

  const closeTutorial = useCallback(() => {
    setTutorialOpen(false);
    if (hasTutorialSearchParams(searchParams)) {
      const next = stripTutorialSearchParams(searchParams);
      const qs = next.toString();
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    }
  }, [pathname, router, searchParams]);

  useEffect(() => {
    const beginner = resolveTutorialBeginnerMode(searchParams);
    setTutorialBeginner(beginner);

    if (hasTutorialSearchParams(searchParams)) {
      setTutorialOpen(true);
      return;
    }

    if (!isPlatformTutorialComplete()) {
      setTutorialOpen(true);
      return;
    }

    setTutorialOpen(false);
  }, [searchParams]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const catalog = await fetchAssetCatalog();
      if (cancelled || !catalog) {
        return;
      }
      setCatalogAssetIds(listSelectableAssetIds(bucketsFromCatalog(catalog)));
      setCatalogDefault(catalog.default_asset_id);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    saveStoredLabAssetId(selectedAssetId);
  }, [selectedAssetId]);

  useEffect(() => {
    if (queryAsset?.trim()) {
      return;
    }
    router.replace(buildAssetHref(pathname, searchParams, selectedAssetId), { scroll: false });
  }, [queryAsset, pathname, router, searchParams, selectedAssetId]);

  useEffect(() => {
    let cancelled = false;
    const ssrMatches =
      initialPayload !== null && isPayloadForSelectedAsset(initialPayload, selectedAssetId);

    if (ssrMatches) {
      setPayload(initialPayload);
      setMode("live");
    } else {
      setMode("loading");
    }

    void (async () => {
      const livePayload = await fetchDisplayPayloadClient(selectedAssetId);
      if (cancelled) {
        return;
      }
      if (livePayload && isPayloadForSelectedAsset(livePayload, selectedAssetId)) {
        setPayload(livePayload);
        setMode("live");
        return;
      }
      if (ssrMatches && initialPayload) {
        return;
      }
      setPayload(null);
      setMode("demo");
    })();

    return () => {
      cancelled = true;
    };
  }, [selectedAssetId, initialPayload]);

  const pillLabel =
    mode === "live"
      ? labDataLivePill(assetMeta)
      : mode === "loading"
        ? LAB_DATA_LOADING_PILL
        : LAB_DATA_DEMO_PILL;
  const pillClass =
    mode === "live" ? "pill live" : mode === "loading" ? "pill loading" : "pill demo sample";

  const assetSwitchParams = useMemo(() => new URLSearchParams(searchParams.toString()), [searchParams]);
  const buildAssetHrefForPicker = useCallback(
    (assetId: string) => buildAssetHref(pathname, assetSwitchParams, assetId),
    [pathname, assetSwitchParams],
  );

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Strategy Lab · {assetMeta.label}</div>
          <h1 className="title">Strategy Lab</h1>
          <nav aria-label="Options asset" style={{ marginTop: 10, maxWidth: 420 }}>
            <LabAssetPicker
              selectedAssetId={selectedAssetId}
              buildAssetHref={buildAssetHrefForPicker}
            />
          </nav>
        </div>
        <div className="tools">
          <span className={pillClass} role="status">
            <span className="dot" aria-hidden="true" />
            {pillLabel}
          </span>
          <Link
            href={buildWorkflowStepHref("confirm", selectedAssetId)}
            className="btn slim primary"
            data-tour="lab-confirm"
          >
            Save your view
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      {mode === "demo" ? (
        <div className="lab-data-banner demo" role="alert">
          <span className="tag amber">Sample</span>
          <div>
            <strong>{LAB_DEMO_BANNER_TITLE}</strong>
            <p>{labDemoBannerBody(assetMeta)}</p>
          </div>
        </div>
      ) : null}

      {mode === "loading" ? (
        <div className="lab-data-banner loading" role="status" aria-live="polite">
          <span className="tag teal">Loading</span>
          <p>{labLoadingBannerBody(assetMeta)}</p>
        </div>
      ) : null}

      {mode === "live" && trustState === "thin_chain" ? (
        <div className="lab-data-banner loading" role="status">
          <span className="tag amber">Thin chain</span>
          <p>
            Options liquidity is limited for {assetMeta.label}. Curves may be approximate — check
            catalog trust notes before trading.
          </p>
        </div>
      ) : null}

      <PendingPaperTradeBanner returnPath={buildWorkflowStepHref("plan", selectedAssetId)} />

      <WorkflowStepper currentStep="compare" assetId={selectedAssetId} />

      <StrategyLabWorkSection displayPayload={payload} dataMode={mode} assetMeta={assetMeta} />

      <PlatformTutorial
        active={tutorialOpen}
        onClose={closeTutorial}
        steps={resolveTutorialSteps(tutorialBeginner)}
        completeHref="/learn?debrief=1"
      />

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
