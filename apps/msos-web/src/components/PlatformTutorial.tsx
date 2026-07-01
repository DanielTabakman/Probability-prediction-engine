"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

import {
  buildTourReturnPath,
  markPlatformTutorialComplete,
  platformTourFeedbackHref,
  PLATFORM_TUTORIAL_STEPS,
  type PlatformTutorialStep,
} from "@/lib/platformTutorial";

type PlatformTutorialProps = {
  active: boolean;
  onClose: () => void;
  steps?: PlatformTutorialStep[];
};

type ViewportRect = {
  top: number;
  left: number;
  width: number;
  height: number;
};

type CardPlacement = {
  top: number;
  left: number;
};

const CARD_GAP = 12;
const VIEWPORT_PADDING = 16;
const CARD_MAX_WIDTH = 360;
const CARD_FALLBACK_HEIGHT = 190;

function measureAnchorViewport(selector: string): ViewportRect | null {
  const node = document.querySelector(selector);
  if (!node) return null;
  const rect = node.getBoundingClientRect();
  return {
    top: rect.top,
    left: rect.left,
    width: rect.width,
    height: rect.height,
  };
}

function scrollAnchorIntoView(selector: string): void {
  const node = document.querySelector(selector);
  if (!node) return;
  node.scrollIntoView({ block: "center", inline: "nearest", behavior: "smooth" });
}

function computeCardPlacement(
  anchor: ViewportRect | null,
  cardHeight: number,
  cardWidth: number,
): CardPlacement {
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  const width = Math.min(cardWidth, viewportWidth - VIEWPORT_PADDING * 2);

  if (!anchor) {
    return {
      top: VIEWPORT_PADDING + 80,
      left: VIEWPORT_PADDING,
    };
  }

  const spaceBelow = viewportHeight - (anchor.top + anchor.height + CARD_GAP);
  const spaceAbove = anchor.top - CARD_GAP;
  const placeAbove = spaceBelow < cardHeight && spaceAbove > spaceBelow;

  let top = placeAbove
    ? anchor.top - CARD_GAP - cardHeight
    : anchor.top + anchor.height + CARD_GAP;

  top = Math.max(
    VIEWPORT_PADDING,
    Math.min(top, viewportHeight - cardHeight - VIEWPORT_PADDING),
  );

  let left = Math.max(VIEWPORT_PADDING, anchor.left);
  left = Math.min(left, viewportWidth - width - VIEWPORT_PADDING);

  return { top, left };
}

function TutorialCard({
  step,
  index,
  total,
  placement,
  cardRef,
  onBack,
  onNext,
  onSkip,
}: {
  step: PlatformTutorialStep;
  index: number;
  total: number;
  placement: CardPlacement;
  cardRef: React.RefObject<HTMLDivElement | null>;
  onBack: () => void;
  onNext: () => void;
  onSkip: () => void;
}) {
  return (
    <div
      ref={cardRef}
      className="platform-tutorial-card"
      role="dialog"
      aria-labelledby={`tutorial-title-${step.id}`}
      style={{ top: placement.top, left: placement.left, maxWidth: CARD_MAX_WIDTH }}
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

function FeedbackPromptCard({
  onShare,
  onDecline,
}: {
  onShare: () => void;
  onDecline: () => void;
}) {
  return (
    <div
      className="platform-tutorial-card platform-tutorial-prompt"
      role="dialog"
      aria-labelledby="tutorial-feedback-prompt-title"
    >
      <div className="platform-tutorial-kicker">Tour complete</div>
      <h3 id="tutorial-feedback-prompt-title">Share quick feedback?</h3>
      <p>
        Totally optional — even one line helps us improve. You can skip and keep exploring where
        you left off.
      </p>
      <div className="platform-tutorial-actions">
        <button type="button" className="btn slim" onClick={onDecline}>
          No thanks — keep exploring
        </button>
        <button type="button" className="btn slim primary" onClick={onShare}>
          Share feedback
        </button>
      </div>
    </div>
  );
}

export function PlatformTutorial({
  active,
  onClose,
  steps = PLATFORM_TUTORIAL_STEPS,
}: PlatformTutorialProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnPath = useMemo(
    () => buildTourReturnPath(pathname, searchParams),
    [pathname, searchParams],
  );

  const [stepIndex, setStepIndex] = useState(0);
  const [feedbackPromptOpen, setFeedbackPromptOpen] = useState(false);
  const [anchor, setAnchor] = useState<ViewportRect | null>(null);
  const [placement, setPlacement] = useState<CardPlacement>({
    top: VIEWPORT_PADDING + 80,
    left: VIEWPORT_PADDING,
  });
  const [mounted, setMounted] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const step = steps[stepIndex];

  const refreshLayout = useCallback(() => {
    if (!step || feedbackPromptOpen) return;
    const nextAnchor = measureAnchorViewport(step.anchor);
    setAnchor(nextAnchor);

    const cardNode = cardRef.current;
    const cardHeight = cardNode?.offsetHeight ?? CARD_FALLBACK_HEIGHT;
    const cardWidth = cardNode?.offsetWidth ?? CARD_MAX_WIDTH;
    setPlacement(computeCardPlacement(nextAnchor, cardHeight, cardWidth));
  }, [feedbackPromptOpen, step]);

  useEffect(() => {
    setMounted(true);
  }, []);

  useLayoutEffect(() => {
    if (!active || !step || feedbackPromptOpen) return;
    scrollAnchorIntoView(step.anchor);
    refreshLayout();
    const afterScroll = window.setTimeout(refreshLayout, 350);
    const afterScrollLong = window.setTimeout(refreshLayout, 700);
    return () => {
      window.clearTimeout(afterScroll);
      window.clearTimeout(afterScrollLong);
    };
  }, [active, feedbackPromptOpen, stepIndex, step, refreshLayout]);

  useEffect(() => {
    if (!active) {
      setStepIndex(0);
      setFeedbackPromptOpen(false);
      return;
    }
    refreshLayout();
    const onViewportChange = () => refreshLayout();
    window.addEventListener("resize", onViewportChange);
    window.addEventListener("scroll", onViewportChange, true);
    return () => {
      window.removeEventListener("resize", onViewportChange);
      window.removeEventListener("scroll", onViewportChange, true);
    };
  }, [active, feedbackPromptOpen, stepIndex, refreshLayout]);

  const dismissTour = useCallback(() => {
    markPlatformTutorialComplete();
    onClose();
  }, [onClose]);

  const handleSkipTour = useCallback(() => {
    dismissTour();
  }, [dismissTour]);

  const handleNext = useCallback(() => {
    if (stepIndex + 1 >= steps.length) {
      setFeedbackPromptOpen(true);
      setAnchor(null);
      return;
    }
    setStepIndex((value) => value + 1);
  }, [stepIndex, steps.length]);

  const handleShareFeedback = useCallback(() => {
    dismissTour();
    router.push(platformTourFeedbackHref(returnPath));
  }, [dismissTour, returnPath, router]);

  const handleDeclineFeedback = useCallback(() => {
    dismissTour();
  }, [dismissTour]);

  if (!active || !mounted) {
    return null;
  }

  if (feedbackPromptOpen) {
    return createPortal(
      <div className="platform-tutorial-root" aria-live="polite">
        <div className="platform-tutorial-scrim platform-tutorial-scrim-blocking" aria-hidden="true" />
        <FeedbackPromptCard onShare={handleShareFeedback} onDecline={handleDeclineFeedback} />
      </div>,
      document.body,
    );
  }

  if (!step) {
    return null;
  }

  return createPortal(
    <div className="platform-tutorial-root" aria-live="polite">
      <div className="platform-tutorial-scrim" aria-hidden="true" />
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
        placement={placement}
        cardRef={cardRef}
        onBack={() => setStepIndex((value) => Math.max(0, value - 1))}
        onNext={handleNext}
        onSkip={handleSkipTour}
      />
    </div>,
    document.body,
  );
}
