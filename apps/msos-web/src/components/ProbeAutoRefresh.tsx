"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export function ProbeAutoRefresh({ intervalMs = 15000 }: { intervalMs?: number }) {
  const router = useRouter();

  useEffect(() => {
    const timer = window.setInterval(() => router.refresh(), intervalMs);
    return () => window.clearInterval(timer);
  }, [intervalMs, router]);

  return <span className="tiny-pill">Auto-refresh {Math.round(intervalMs / 1000)}s</span>;
}
