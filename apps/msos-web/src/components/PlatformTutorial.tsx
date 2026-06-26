"use client";

import { useCallback, useEffect, useState } from "react";
import { createPortal } from "react-dom";

import {
  markPlatformTutorialComplete,
  PLATFORM_TUTORIAL_STEPS,
  type PlatformTutorialStep,
} from "@/lib/platformTutorial";

type PlatformTutorialProps = {
  active: boolean;
  onClose: () => void;
  steps?: PlatformTutorialStep[];
};

type AnchorRect = {
  top: number;
  left: number;
  width: number;
  height: number;
};

function measureAnchor(selector: string): AnchorRect | null {
  const node = document.querySelector(selector);
  if (!node) return null;
  const rect = node.getBoundingClientRect();
  return {
    top: rect.top + window.scrollY,
    left: rect.left + window.scrollX,
    width: rect.width,
    height: rect.height,
  };
}

function TutorialCard({
  step,
  index,
  total,
  anchor,
  onBack,
  onNext,
  onSkip,
}: {
  step: PlatformTutorialStep;
  index: number;
  total: number;
  anchor: AnchorRect | null;
  onBack: () => void;
  onNext: () => void;
  onSkip: () => void;
}) {
  const top = anchor ? anchor.top + anchor.height + 12 : 120;
  const left = anchor ? Math.max(16, anchor.left) : 24;

  return (
    <div
      className="platform-tutorial-card"
      role="dialog"
      aria-labelledby={`tutorial-title-${step.id}`}
      style={{ top, left, maxWidth: 360 }}
    >
      <div className="platform-tutorial-kicker">
        Step {index + 1} of {total}
      </div>
      <h3 id={`tutorial-title-${step.id}`}>{step.title}</h3>
      <p>{step.body}</p>
      <div className="platform-tutorial-actions">
        {index > 0 ? (
          <button type="button" className="btn slim" onClick={onBack}>
            Back
          </button>
        ) : (
          <button type="button" className="btn slim" onClick={onSkip}>
            Skip tour
          </button>
        )}
        <button type="button" className="btn slim primary" onClick={onNext}>
          {index + 1 >= total ? "Done" : "Next"}
        </button>
      </div>
    </div>
  );
}

export function PlatformTutorial({ active, onClose, steps = PLATFORM_TUTORIAL_STEPS }: PlatformTutorialProps) {
  const [stepIndex, setStepIndex] = useState(0);
  const [anchor, setAnchor] = useState<AnchorRect | null>(null);
  const [mounted, setMounted] = useState(false);

  const step = steps[stepIndex];

  const refreshAnchor = useCallback(() => {
    if (!step) return;
    const node = document.querySelector(step.anchor);
    if (node) {
      node.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    setAnchor(measureAnchor(step.anchor));
  }, [step]);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!active) {
      setStepIndex(0);
      return;
    }
    refreshAnchor();
    const onResize = () => refreshAnchor();
    window.addEventListener("resize", onResize);
    window.addEventListener("scroll", onResize, true);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("scroll", onResize, true);
    };
  }, [active, stepIndex, refreshAnchor, steps]);

  const finish = useCallback(() => {
    markPlatformTutorialComplete();
    onClose();
  }, [onClose]);

  const handleNext = useCallback(() => {
    if (stepIndex + 1 >= steps.length) {
      finish();
      return;
    }
    setStepIndex((value) => value + 1);
  }, [finish, stepIndex, steps.length]);

  if (!active || !mounted || !step) {
    return null;
  }

  return createPortal(
    <div className="platform-tutorial-root" aria-live="polite">
      <div className="platform-tutorial-scrim" onClick={finish} aria-hidden="true" />
      {anchor ? (
        <div
          className="platform-tutorial-spotlight"
          style={{
            top: anchor.top - 6,
            left: anchor.left - 6,
            width: anchor.width + 12,
            height: anchor.height + 12,
          }}
        />
      ) : null}
      <TutorialCard
        step={step}
        index={stepIndex}
        total={steps.length}
        anchor={anchor}
        onBack={() => setStepIndex((value) => Math.max(0, value - 1))}
        onNext={handleNext}
        onSkip={finish}
      />
    </div>,
    document.body,
  );
}
