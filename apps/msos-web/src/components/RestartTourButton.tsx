"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState, type ReactNode } from "react";

import { useNavigationProgress } from "@/components/NavigationProgressProvider";
import { warmStrategyLabEntry } from "@/lib/prefetchStrategyLab";
import { clearPlatformTutorialComplete, strategyLabForcedTourHref } from "@/lib/platformTutorial";

type RestartTourButtonProps = {
  className?: string;
  children: ReactNode;
  beginner?: boolean;
};

/** Clears tour completion and opens Strategy Lab — only use for explicit restart CTAs. */
export function RestartTourButton({ className, children, beginner = false }: RestartTourButtonProps) {
  const router = useRouter();
  const { start } = useNavigationProgress();
  const [pending, setPending] = useState(false);
  const tourHref = strategyLabForcedTourHref(beginner);

  const handlePointerEnter = useCallback(() => {
    warmStrategyLabEntry(router, tourHref);
  }, [router, tourHref]);

  return (
    <button
      type="button"
      className={[className, pending ? "btn-pending" : ""].filter(Boolean).join(" ")}
      aria-busy={pending || undefined}
      disabled={pending}
      onPointerEnter={handlePointerEnter}
      onClick={() => {
        setPending(true);
        start();
        clearPlatformTutorialComplete();
        router.push(tourHref);
      }}
    >
      {pending ? <span className="btn-feedback" aria-hidden="true" /> : null}
      {pending ? "Opening tour…" : children}
    </button>
  );
}
