import { RouteLoadingPanel } from "@/components/RouteLoadingPanel";

export default function StrategyLabLoading() {
  return (
    <RouteLoadingPanel
      title="Opening Strategy Lab…"
      subtitle="Fetching live market data. The guided tour starts as soon as the page is ready."
    />
  );
}
