"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

import { logProductUsage } from "@/lib/logProductUsage";

const SESSION_KEY = "ppe_msos_session_started";

export function ProductUsageBeacon() {
  const pathname = usePathname();

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!sessionStorage.getItem(SESSION_KEY)) {
      sessionStorage.setItem(SESSION_KEY, new Date().toISOString());
      logProductUsage({ event_name: "session_start", path: pathname });
    }
  }, [pathname]);

  useEffect(() => {
    logProductUsage({ event_name: "page_view", path: pathname });
  }, [pathname]);

  return null;
}
