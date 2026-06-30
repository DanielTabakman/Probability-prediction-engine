"use client";

import type { ReactNode } from "react";

import { logProductUsage } from "@/lib/logProductUsage";

type DistributionExportLinkProps = {
  href: string;
  assetId: string;
  className?: string;
  children: ReactNode;
};

export function DistributionExportLink({ href, assetId, className, children }: DistributionExportLinkProps) {
  return (
    <a
      href={href}
      className={className}
      download
      onClick={() => {
        logProductUsage({
          event_name: "distribution_export_click",
          path: href,
          asset_id: assetId,
        });
      }}
    >
      {children}
    </a>
  );
}
