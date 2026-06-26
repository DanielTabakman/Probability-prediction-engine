import type { PlanLeg } from "@/data/expressionPlanningFixtures";

function instrumentKind(instrument: string): "put" | "call" | "other" {
  const lower = instrument.toLowerCase();
  if (lower.includes("put")) return "put";
  if (lower.includes("call")) return "call";
  return "other";
}

/** Plain-language hover / long-press hint for one leg row (display only). */
export function planLegTooltip(leg: PlanLeg): string {
  const kind = instrumentKind(leg.instrument);
  const strike = leg.strike.replace(/^Strike\s*/i, "").trim() || leg.strike;
  if (leg.side === "BUY") {
    if (kind === "put") {
      return `Buy ${leg.instrument} at ${strike} — you pay premium for downside protection near that price.`;
    }
    if (kind === "call") {
      return `Buy ${leg.instrument} at ${strike} — you pay premium to participate if BTC rises past that level.`;
    }
    return `Buy ${leg.instrument} at ${strike} — premium paid for this leg of the spread.`;
  }
  if (kind === "put") {
    return `Sell ${leg.instrument} at ${strike} — you collect premium and take risk if BTC falls sharply.`;
  }
  if (kind === "call") {
    return `Sell ${leg.instrument} at ${strike} — you collect premium and take risk if BTC rallies past that level.`;
  }
  return `Sell ${leg.instrument} at ${strike} — premium collected on this leg of the spread.`;
}
