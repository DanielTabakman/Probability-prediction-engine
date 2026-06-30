"use client";

import { useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";

import { clearPlatformTutorialComplete, strategyLabForcedTourHref } from "@/lib/platformTutorial";

type RestartTourButtonProps = {
  className?: string;
  children: ReactNode;
  beginner?: boolean;
};

/** Clears tour completion and opens Strategy Lab — only use for explicit restart CTAs. */
export function RestartTourButton({ className, children, beginner = false }: RestartTourButtonProps) {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  return (
    <button
      type="button"
      className={[className, pending ? "btn-pending" : ""].filter(Boolean).join(" ")}
      aria-busy={pending || undefined}
      disabled={pending}
      onClick={() => {
        setPending(true);
        clearPlatformTutorialComplete();
        router.push(strategyLabForcedTourHref(beginner));
      }}
    >
      {pending ? <span className="btn-feedback" aria-hidden="true" /> : null}
      {pending ? "Opening tour…" : children}
    </button>
  );
}
