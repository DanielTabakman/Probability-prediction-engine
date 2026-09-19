"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  RegionBetGuidedShellPanel,
  type RegionBetGuidedAssetOption,
} from "@/components/RegionBetGuidedShellPanel";
import { RegionBetResumeCard } from "@/components/RegionBetResumeCard";
import {
  REGION_BET_GUIDED_SHELL_STEPS,
  applyRegionBetGuidedShellPatch,
  buildRegionBetGuidedShellSnapshot,
  createRegionBetGuidedDraft,
  isRegionBetGuidedDraftPersistable,
  nextRegionBetGuidedShellStep,
  previousRegionBetGuidedShellStep,
  regionBetGuidedShellStepIndex,
  withRegionBetGuidedShellStep,
  type RegionBetGuidedShellPatch,
  type RegionBetGuidedShellStep,
} from "@/lib/regionBetGuidedShell";
import {
  REGION_BET_PERSISTENCE_LABEL,
  persistRegionBet,
  type RegionBetContract,
} from "@/lib/regionBet";
import { confirmRegionBetPayoff } from "@/lib/regionBetPayoff";
import {
  createCleanStartRegionBetResume,
  fetchRegionBetResume,
  type RegionBetResumeState,
} from "@/lib/regionBetResume";

const DEFAULT_ASSET_OPTIONS: RegionBetGuidedAssetOption[] = [
  { asset_id: "ETH", symbol: "ETH", venue: "Deribit", spot_usd: 3000 },
  { asset_id: "BTC", symbol: "BTC", venue: "Deribit", spot_usd: 65000 },
  { asset_id: "NVDA", symbol: "NVDA", venue: "equity options chain", spot_usd: 120 },
];

type SaveState = "idle" | "saving" | "saved" | "confirmed" | "invalid" | "offline";

type RegionBetGuidedShellProps = {
  initialRegionBet?: RegionBetContract | null;
  initialStep?: RegionBetGuidedShellStep;
  assetOptions?: RegionBetGuidedAssetOption[];
};

export function RegionBetGuidedShell({
  initialRegionBet = null,
  initialStep = "asset",
  assetOptions = DEFAULT_ASSET_OPTIONS,
}: RegionBetGuidedShellProps) {
  const [step, setStep] = useState<RegionBetGuidedShellStep>(initialStep);
  const [draft, setDraft] = useState<RegionBetContract>(() =>
    createRegionBetGuidedDraft(initialRegionBet),
  );
  const [hydrated, setHydrated] = useState(Boolean(initialRegionBet));
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [resume, setResume] = useState<RegionBetResumeState>(() =>
    initialRegionBet
      ? {
          schema_version: 1,
          kind: "region_bet_session_resume",
          mode: "resume",
          reason: "valid",
          regionBet: createRegionBetGuidedDraft(initialRegionBet),
          step: initialStep,
          clean_start_available: true,
          paper_only: true,
          limitation:
            "Paper workflow only. Resume restores your saved Region Bet. Not financial advice, not a recommendation, and not order execution.",
        }
      : createCleanStartRegionBetResume("missing"),
  );

  const applyResumeState = useCallback((state: RegionBetResumeState) => {
    setResume(state);
    if (state.mode === "resume" && state.regionBet) {
      setDraft(createRegionBetGuidedDraft(state.regionBet));
      setStep(state.step);
      return;
    }
    setDraft(createRegionBetGuidedDraft());
    setStep("asset");
  }, []);

  useEffect(() => {
    let cancelled = false;
    void fetchRegionBetResume().then((state) => {
      if (cancelled) return;
      applyResumeState(state);
      setHydrated(true);
    });
    return () => {
      cancelled = true;
    };
  }, [applyResumeState]);

  const currentIndex = regionBetGuidedShellStepIndex(step);
  const snapshot = useMemo(() => buildRegionBetGuidedShellSnapshot(draft), [draft]);

  const updateDraft = useCallback((patch: RegionBetGuidedShellPatch) => {
    setDraft((current) => applyRegionBetGuidedShellPatch(current, patch));
    setSaveState("idle");
  }, []);

  const persistDraft = useCallback(async () => {
    if (!isRegionBetGuidedDraftPersistable(draft)) {
      setSaveState("invalid");
      return false;
    }
    setSaveState("saving");
    const saved = await persistRegionBet(draft);
    setSaveState(saved ? "saved" : "offline");
    return true;
  }, [draft]);

  const confirmPayoff = useCallback(async () => {
    const confirmed = confirmRegionBetPayoff(draft, { confirmed: true });
    if (!confirmed) {
      setSaveState("invalid");
      return;
    }
    setSaveState("saving");
    const saved = await persistRegionBet(confirmed, { confirmPayoff: true });
    setDraft(confirmed);
    setSaveState(saved ? "confirmed" : "offline");
  }, [draft]);

  const goPrevious = useCallback(() => {
    setStep((current) => previousRegionBetGuidedShellStep(current));
  }, []);

  const goNext = useCallback(async () => {
    const saved = await persistDraft();
    if (saved) {
      setStep((current) => nextRegionBetGuidedShellStep(current));
    }
  }, [persistDraft]);

  useEffect(() => {
    setDraft((current) =>
      current.guided_step === step ? current : withRegionBetGuidedShellStep(current, step),
    );
  }, [step]);

  const resumeSavedDraft = useCallback(() => {
    if (resume.mode === "resume" && resume.regionBet) {
      applyResumeState(resume);
    }
  }, [applyResumeState, resume]);

  const startCleanDraft = useCallback(() => {
    setDraft(createRegionBetGuidedDraft());
    setStep("asset");
    setSaveState("idle");
  }, []);

  const atFirstStep = currentIndex === 0;
  const atLastStep = currentIndex === REGION_BET_GUIDED_SHELL_STEPS.length - 1;
  const statusLabel =
    saveState === "saving"
      ? "Saving draft..."
      : saveState === "saved"
        ? REGION_BET_PERSISTENCE_LABEL
        : saveState === "confirmed"
          ? "Active paper Region Bet saved with a frozen entry snapshot."
        : saveState === "invalid"
          ? "Draft needs a valid region, selected paper expression, and explicit confirmation."
          : saveState === "offline"
            ? "Saved locally; server sync will retry from the Region Bet contract."
            : hydrated
              ? "Draft loaded from the Region Bet contract."
              : "Loading Region Bet draft...";

  return (
    <section className="work strategy-lab-work" aria-label="Region Bet guided shell">
      {hydrated ? (
        <RegionBetResumeCard
          resume={resume}
          onResume={resumeSavedDraft}
          onCleanStart={startCleanDraft}
        />
      ) : null}
      <div className="panel chart">
        <div className="panel-head">
          <div>
            <h2>Region Bet</h2>
            <div className="panel-sub">Guided draft shell - simulation only.</div>
          </div>
          <span className="tag">Guided</span>
        </div>
        <nav className="workflow-stepper" aria-label="Region Bet workflow">
          {REGION_BET_GUIDED_SHELL_STEPS.map((item, index) => {
            const active = item.id === step;
            const done = index < currentIndex;
            const className = [
              "workflow-step",
              active ? "active" : undefined,
              done ? "done" : undefined,
            ]
              .filter(Boolean)
              .join(" ");
            return (
              <button
                key={item.id}
                type="button"
                className={className}
                aria-current={active ? "step" : undefined}
                onClick={() => setStep(item.id)}
              >
                <span className="workflow-step-num" aria-hidden="true">
                  {index + 1}
                </span>
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      <RegionBetGuidedShellPanel
        step={step}
        draft={draft}
        snapshot={snapshot}
        assetOptions={assetOptions}
        onDraftChange={updateDraft}
        onConfirmPayoff={confirmPayoff}
        payoffSaveStatus={saveState === "confirmed" ? "saved" : saveState}
      />

      <div className="panel outcome">
        <div className="decision-strip">
          <div>
            <strong>{statusLabel}</strong>
            <p>
              Retained context: {snapshot.symbol ?? snapshot.asset_id}, expiry{" "}
              {snapshot.expiry_utc.slice(0, 10)}, region{" "}
              {snapshot.selected_region.price_min_usd} to{" "}
              {snapshot.selected_region.price_max_usd}
              {draft.selected_expression_ref
                ? `, paper expression ${draft.selected_expression_ref.expression_id}`
                : ""}.
            </p>
          </div>
          <div className="lab-setup-actions">
            <button
              type="button"
              className="btn slim"
              onClick={goPrevious}
              disabled={atFirstStep}
            >
              Back
            </button>
            <button
              type="button"
              className="btn slim primary"
              onClick={atLastStep ? persistDraft : goNext}
              disabled={saveState === "saving"}
            >
              {atLastStep ? "Save draft" : "Next"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
