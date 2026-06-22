/** User-facing degraded / status messages — hide internal errors from the UI.
 *  Canon: docs/SOP/MSOS_PUBLIC_COPY_V1.md
 */

export function friendlySnapshotFeedMessage(rawReason?: string | null): string {
  if (!rawReason) {
    return "Saved views aren't available right now. Strategy Lab live charts still work.";
  }
  const lower = rawReason.toLowerCase();
  if (
    lower.includes("bindings") ||
    lower.includes("cannot find module") ||
    lower.includes("snapshot database") ||
    lower.includes("not readable") ||
    lower.includes("ppe_snapshot")
  ) {
    return "Saved history isn't connected yet — we're working on it. Live options data in Strategy Lab still works.";
  }
  return "Saved views aren't available right now.";
}

export const DEMO_FOOTER =
  "Research preview — paper trading only. Nothing here sends a live order.";

export const WORKSPACE_SAVED_LABEL = "Saved to your workspace";

export const SNAPSHOT_SOURCE_LABEL = "From your saved views";

export const WORKFLOW_SOURCE_LABEL = "Your workspace + saved views";
