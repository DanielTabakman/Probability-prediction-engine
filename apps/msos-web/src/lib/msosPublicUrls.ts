/** Public MSOS URLs — display only; no auth logic in TypeScript. */

const DEFAULT_SIGN_IN_URL = "https://app.marketstructureos.com";

export const MSOS_ROUTES = {
  home: "/",
  commandCenter: "/command-center",
  strategyLab: "/strategy-lab",
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
