"use client";

import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

/** Shown while Strategy Lab mounts and tour anchor targets become available. */
export function TourPreparingOverlay({ active }: { active: boolean }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!active || !mounted) {
    return null;
  }

  return createPortal(
    <div className="tour-preparing-overlay" role="status" aria-live="polite" aria-busy="true">
      <div className="tour-preparing-card">
        <span className="route-loading-spinner" aria-hidden="true" />
        <p className="tour-preparing-title">Preparing guided tour…</p>
        <p className="tour-preparing-subtitle">Loading Strategy Lab and highlighting the first step.</p>
      </div>
    </div>,
    document.body,
  );
}
