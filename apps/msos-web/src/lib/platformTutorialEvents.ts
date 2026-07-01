/** Cross-component signals for play-gated tour steps (belief nudge, etc.). */

import type { PlatformTutorialPlayAction } from "@/lib/platformTutorial";

export const PLATFORM_TOUR_PLAY_EVENT = "msos.platform.tutorial.play";

export type PlatformTourPlayDetail = {
  action: PlatformTutorialPlayAction;
};

export function notifyPlatformTourPlayAction(action: PlatformTutorialPlayAction): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent<PlatformTourPlayDetail>(PLATFORM_TOUR_PLAY_EVENT, { detail: { action } }),
  );
}
