type RouteLoadingPanelProps = {
  title: string;
  subtitle?: string;
};

/** Full-viewport loading state for slow App Router transitions. */
export function RouteLoadingPanel({ title, subtitle }: RouteLoadingPanelProps) {
  return (
    <div className="route-loading-panel" role="status" aria-live="polite" aria-busy="true">
      <div className="route-loading-card">
        <span className="route-loading-spinner" aria-hidden="true" />
        <h1 className="route-loading-title">{title}</h1>
        {subtitle ? <p className="route-loading-subtitle">{subtitle}</p> : null}
      </div>
    </div>
  );
}
