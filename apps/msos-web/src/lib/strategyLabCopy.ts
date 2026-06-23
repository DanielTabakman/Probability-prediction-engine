/** Strategy Lab data-mode copy — live vs sample (fixtures). */

export type LabDataMode = "loading" | "live" | "demo";

export const LAB_DATA_LIVE_PILL = "Live · Deribit options";
export const LAB_DATA_DEMO_PILL = "Sample data · not live";
export const LAB_DATA_LOADING_PILL = "Loading live data…";

export const LAB_DEMO_BANNER_TITLE = "Sample mode — not live market data";
export const LAB_DEMO_BANNER_BODY =
  "The numbers and chart below use placeholder fixtures for layout preview. Refresh the page or check your connection — live BTC options from Deribit load automatically when available.";

export const LAB_LOADING_BANNER_BODY =
  "Fetching live BTC options from Deribit. Metrics and chart will update in a moment.";

export const LAB_LIVE_BANNER_BODY =
  "Spot, range, and curves come from live Deribit option quotes for the selected expiry.";
