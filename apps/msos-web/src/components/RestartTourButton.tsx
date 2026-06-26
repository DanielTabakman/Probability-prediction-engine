"use client";

import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { clearPlatformTutorialComplete, strategyLabForcedTourHref } from "@/lib/platformTutorial";

type RestartTourButtonProps = {
  className?: string;
  children: ReactNode;
  beginner?: boolean;
};

/** Clears tour completion and opens Strategy Lab — only use for explicit restart CTAs. */
export function RestartTourButton({ className, children, beginner = false }: RestartTourButtonProps) {
  const router = useRouter();

  return (
    <button
      type="button"
      className={className}
      onClick={() => {
        clearPlatformTutorialComplete();
        router.push(strategyLabForcedTourHref(beginner));
      }}
    >
      {children}
    </button>
  );
}
