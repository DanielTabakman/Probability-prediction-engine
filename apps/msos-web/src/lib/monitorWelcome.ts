/** One-time monitor welcome after first paper trade (browser only). */

export const MONITOR_WELCOME_DISMISSED_KEY = "msos.monitor.welcomeDismissed.v1";
export const MONITOR_WELCOME_QUERY = "welcome";

export function isMonitorWelcomeDismissed(): boolean {
  if (typeof window === "undefined") return true;
  try {
    return window.localStorage.getItem(MONITOR_WELCOME_DISMISSED_KEY) === "1";
  } catch {
    return true;
  }
}

export function markMonitorWelcomeDismissed(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(MONITOR_WELCOME_DISMISSED_KEY, "1");
  } catch {
    /* ignore */
  }
}

export function shouldShowMonitorWelcome(
  paperTradeCount: number,
  welcomeQuery: boolean,
): boolean {
  if (paperTradeCount < 1) return false;
  if (welcomeQuery) return true;
  if (paperTradeCount === 1 && !isMonitorWelcomeDismissed()) return true;
  return false;
}
