"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { StrategyLabWorkSection } from "@/components/StrategyLabWorkSection";
import { PlatformTutorial } from "@/components/PlatformTutorial";
import { PendingPaperTradeBanner } from "@/components/PendingPaperTradeBanner";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import {
  DEFAULT_LAB_ASSET_ID,
  LAB_ASSET_QUERY_PARAM,
  SUPPORTED_LAB_ASSET_IDS,
  fetchDisplayPayloadClient,
  normalizeLabAssetId,
  resolveDisplayAssetMeta,
  type DisplayPayload,
  type LabAssetId,
} from "@/lib/ppeDisplayPayload";
import {
  LAB_DATA_DEMO_PILL,
  LAB_DATA_LIVE_PILL,
  LAB_DATA_LOADING_PILL,
  LAB_DEMO_BANNER_BODY,
  LAB_DEMO_BANNER_TITLE,
  LAB_LOADING_BANNER_BODY,
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

function resolveInitialMode(initialPayload: DisplayPayload | null): LabDataMode {
  return initialPayload ? "live" : "loading";
}

function buildAssetHref(
  pathname: string,
  searchParams: URLSearchParams,
  assetId: LabAssetId,
): string {
  const params = new URLSearchParams(searchParams.toString());
  if (assetId === DEFAULT_LAB_ASSET_ID) {
    params.delete(LAB_ASSET_QUERY_PARAM);
  } else {
    params.set(LAB_ASSET_QUERY_PARAM, assetId);
  }
  const qs = params.toString();
  return qs ? `${pathname}?${qs}` : pathname;
}

export function StrategyLabClientShell({ initialPayload }: StrategyLabClientShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedAssetId = normalizeLabAssetId(searchParams.get(LAB_ASSET_QUERY_PARAM));
  const [payload, setPayload] = useState<DisplayPayload | null>(initialPayload);
  const [mode, setMode] = useState<LabDataMode>(() => resolveInitialMode(initialPayload));
  const [tutorialOpen, setTutorialOpen] = useState(false);
  const [tutorialBeginner, setTutorialBeginner] = useState(false);
  const assetMeta = useMemo(
    () => resolveDisplayAssetMeta(payload, selectedAssetId),
    [payload, selectedAssetId],
  );

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
    setMode("loading");

    void (async () => {
      const livePayload = await fetchDisplayPayloadClient(selectedAssetId);
      if (cancelled) {
        return;
      }
      if (livePayload) {
        setPayload(livePayload);
        setMode("live");
        return;
      }
      if (selectedAssetId === DEFAULT_LAB_ASSET_ID && initialPayload) {
        setPayload(initialPayload);
        setMode("live");
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
    mode === "live" ? LAB_DATA_LIVE_PILL : mode === "loading" ? LAB_DATA_LOADING_PILL : LAB_DATA_DEMO_PILL;
  const pillClass =
    mode === "live" ? "pill live" : mode === "loading" ? "pill loading" : "pill demo sample";

  const assetSwitchParams = useMemo(() => new URLSearchParams(searchParams.toString()), [searchParams]);

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Strategy Lab · {assetMeta.label}</div>
          <h1 className="title">Strategy Lab</h1>
          <nav
            className="belief-axis-pair"
            aria-label="Options asset"
            style={{ marginTop: 10, maxWidth: 300 }}
            data-tour="lab-asset"
          >
            {SUPPORTED_LAB_ASSET_IDS.map((assetId) => {
              const active = assetId === selectedAssetId;
              return (
                <Link
                  key={assetId}
                  href={buildAssetHref(pathname, assetSwitchParams, assetId)}
                  className={`belief-preset${active ? " active" : ""}`}
                  aria-current={active ? "page" : undefined}
                  data-asset={assetId}
                >
                  {assetId}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="tools">
          <span className={pillClass} role="status">
            <span className="dot" aria-hidden="true" />
            {pillLabel}
          </span>
          <Link
            href={
              selectedAssetId === DEFAULT_LAB_ASSET_ID
                ? "/strategy-lab/confirm"
                : `/strategy-lab/confirm?${LAB_ASSET_QUERY_PARAM}=${selectedAssetId}`
            }
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
            <p>{LAB_DEMO_BANNER_BODY}</p>
          </div>
        </div>
      ) : null}

      {mode === "loading" ? (
        <div className="lab-data-banner loading" role="status" aria-live="polite">
          <span className="tag teal">Loading</span>
          <p>{LAB_LOADING_BANNER_BODY}</p>
        </div>
      ) : null}

      <PendingPaperTradeBanner returnPath="/strategy-lab/expression" />

      <StrategyLabWorkSection displayPayload={payload} dataMode={mode} />

      <PlatformTutorial
        active={tutorialOpen}
        onClose={closeTutorial}
        steps={resolveTutorialSteps(tutorialBeginner)}
      />

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
