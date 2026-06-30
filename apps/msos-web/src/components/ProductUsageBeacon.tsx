"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

import { logProductUsage } from "@/lib/logProductUsage";

export function ProductUsageBeacon() {
  const pathname = usePathname();

  useEffect(() => {
    logProductUsage({ event_name: "page_view", path: pathname });
  }, [pathname]);

  return null;
}
