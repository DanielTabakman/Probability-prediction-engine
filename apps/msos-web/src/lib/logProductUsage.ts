export type ProductUsagePayload = {
  event_name: string;
  path?: string;
  asset_id?: string;
  source?: string;
};

export function logProductUsage(payload: ProductUsagePayload): void {
  if (typeof window === "undefined") return;
  const body = JSON.stringify({ ...payload, source: payload.source ?? "msos-web" });
  try {
    void fetch("/api/usage/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
    });
  } catch {
    // advisory telemetry only
  }
}
