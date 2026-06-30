"use client";

import { useEffect, useState } from "react";

const POLL_MS = 100;
const FALLBACK_MS = 8000;

/** Poll until a tour anchor exists in the DOM, with a hard timeout fallback. */
export function useTourAnchorsReady(active: boolean, anchorSelector: string): boolean {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!active) {
      setReady(false);
      return;
    }

    if (!anchorSelector) {
      setReady(true);
      return;
    }

    let cancelled = false;

    const hasAnchor = () => Boolean(document.querySelector(anchorSelector));

    if (hasAnchor()) {
      setReady(true);
      return;
    }

    setReady(false);

    const interval = window.setInterval(() => {
      if (cancelled) {
        return;
      }
      if (hasAnchor()) {
        setReady(true);
        window.clearInterval(interval);
      }
    }, POLL_MS);

    const timeout = window.setTimeout(() => {
      if (!cancelled) {
        setReady(true);
      }
    }, FALLBACK_MS);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
      window.clearTimeout(timeout);
    };
  }, [active, anchorSelector]);

  return ready;
}
