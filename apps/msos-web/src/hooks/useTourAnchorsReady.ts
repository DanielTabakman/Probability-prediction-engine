"use client";

import { useEffect, useState } from "react";

const FALLBACK_MS = 8000;

/** Wait until a tour anchor exists in the DOM, with a hard timeout fallback. */
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

    const markReady = () => {
      if (!cancelled) {
        setReady(true);
      }
    };

    if (hasAnchor()) {
      setReady(true);
      return;
    }

    setReady(false);

    const observer = new MutationObserver(() => {
      if (hasAnchor()) {
        markReady();
        observer.disconnect();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });

    const raf = window.requestAnimationFrame(() => {
      if (hasAnchor()) {
        markReady();
        observer.disconnect();
      }
    });

    const timeout = window.setTimeout(markReady, FALLBACK_MS);

    return () => {
      cancelled = true;
      observer.disconnect();
      window.cancelAnimationFrame(raf);
      window.clearTimeout(timeout);
    };
  }, [active, anchorSelector]);

  return ready;
}
