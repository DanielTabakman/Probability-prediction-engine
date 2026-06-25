/** Safe monitor navigation after destructive paper-trade actions. */

export function monitorUrlAfterDelete(title: string): string {
  const trimmed = title.trim() || "Paper trade";
  return `/monitor?deleted=1&title=${encodeURIComponent(trimmed)}`;
}

/** Hard navigation — avoids Next.js soft-nav re-fetching a deleted `/monitor/paper/[id]` route. */
export function goToMonitorAfterDelete(title: string): void {
  window.location.assign(monitorUrlAfterDelete(title));
}

export function goToMonitorAfterDeleteFromRouter(
  router: { replace: (href: string) => void },
  title: string,
  pathname: string,
): void {
  const url = monitorUrlAfterDelete(title);
  if (pathname.startsWith("/monitor/paper/")) {
    goToMonitorAfterDelete(title);
    return;
  }
  router.replace(url);
}
