/**
 * Belief tuning UX copy — explains demo bounds (math stays in Python).
 */

import { BELIEF_TUNING_BOUNDS } from "@/lib/beliefTuning";

const fwd = BELIEF_TUNING_BOUNDS.forward_mult;
const vol = BELIEF_TUNING_BOUNDS.vol_mult;

export const BELIEF_TUNING_BOUNDS_NOTE =
  `Sliders re-scale the market lognormal curve: center shift ${Math.round((1 - fwd.min) * 100)}–${Math.round((fwd.max - 1) * 100)}% versus forward, vol ${vol.min}–${vol.max}× ATM. That matches what the belief overlay API can compute from live Deribit quotes — not a free-form tail model.`;

export const BELIEF_TAIL_LIMIT_NOTE =
  "Unlimited upside or deep crash views need a custom distribution (not a simple center/vol shift). Use Request research beta for fat-tail / skew overlays — on the roadmap for advanced belief mode.";
