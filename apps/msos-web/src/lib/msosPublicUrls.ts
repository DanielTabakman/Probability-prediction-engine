/** Public MSOS URLs — display only; no auth logic in TypeScript. */

import { stashPostAuthReturnPath } from "@/lib/postAuthReturn";

const DEFAULT_SIGN_IN_URL = "https://app.marketstructureos.com";

export const MSOS_ROUTES = {
  home: "/",
  commandCenter: "/command-center",
  strategyLab: "/strategy-lab",
  exposure: "/exposure",
  optionsHorizon: "/options-horizon",
  monitor: "/monitor",
  history: "/history",
  learn: "/learn",
} as const;

/** Private app / Cloudflare Access entry (NEXT_PUBLIC_MSOS_SIGN_IN_URL or legacy alias). */
export function resolveSignInUrl(): string {
  const raw = (
    process.env.NEXT_PUBLIC_MSOS_SIGN_IN_URL ??
    process.env.NEXT_PUBLIC_PPE_PRIVATE_APP_URL ??
    ""
  ).trim();
  if (raw && raw.toLowerCase().startsWith("https://")) {
    return raw;
  }
  return DEFAULT_SIGN_IN_URL;
}

/** Sign-in URL with post-auth return path (browser only). */
export function resolveSignInUrlWithReturn(returnPath: string): string {
  const base = resolveSignInUrl();
  if (typeof window === "undefined") {
    return base;
  }
  const path = returnPath.startsWith("/") ? returnPath : `/${returnPath}`;
  stashPostAuthReturnPath(path);
  const returnTo = `${window.location.origin}${path}`;
  const separator = base.includes("?") ? "&" : "?";
  return `${base}${separator}returnTo=${encodeURIComponent(returnTo)}`;
}
