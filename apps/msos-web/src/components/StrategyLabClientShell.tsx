"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { StrategyLabWorkSection } from "@/components/StrategyLabWorkSection";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import {
  fetchDisplayPayloadClient,
  type DisplayPayload,
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

type StrategyLabClientShellProps = {
  initialPayload: DisplayPayload | null;
};

function resolveInitialMode(initialPayload: DisplayPayload | null): LabDataMode {
  return initialPayload ? "live" : "loading";
}

export function StrategyLabClientShell({ initialPayload }: StrategyLabClientShellProps) {
  const [payload, setPayload] = useState<DisplayPayload | null>(initialPayload);
  const [mode, setMode] = useState<LabDataMode>(() => resolveInitialMode(initialPayload));

  useEffect(() => {
    if (initialPayload) {
      setPayload(initialPayload);
      setMode("live");
      return;
    }

    let cancelled = false;
    void (async () => {
      const livePayload = await fetchDisplayPayloadClient();
      if (cancelled) {
        return;
      }
      if (livePayload) {
        setPayload(livePayload);
        setMode("live");
      } else {
        setPayload(null);
        setMode("demo");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [initialPayload]);

  const pillLabel =
    mode === "live" ? LAB_DATA_LIVE_PILL : mode === "loading" ? LAB_DATA_LOADING_PILL : LAB_DATA_DEMO_PILL;
  const pillClass =
    mode === "live" ? "pill live" : mode === "loading" ? "pill loading" : "pill demo sample";

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Strategy Lab · BTC options</div>
          <h1 className="title">Strategy Lab</h1>
        </div>
        <div className="tools">
          <span className={pillClass} role="status">
            <span className="dot" aria-hidden="true" />
            {pillLabel}
          </span>
          <span className="btn slim">Share</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
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

      <StrategyLabWorkSection displayPayload={payload} dataMode={mode} />

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
