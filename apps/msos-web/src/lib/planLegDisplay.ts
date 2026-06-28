import type { PlanLeg } from "@/data/expressionPlanningFixtures";

/** Relabel BTC-default API legs for the selected asset (display only). */
export function relabelPlanLegsForAsset(legs: PlanLeg[], assetId: string): PlanLeg[] {
  const ticker = assetId.trim().toUpperCase();
  if (!ticker || ticker === "BTC") {
    return legs;
  }
  const btcPrefix = /^BTC\b/i;
  return legs.map((leg) => {
    if (!btcPrefix.test(leg.instrument)) {
      return leg;
    }
    return {
      ...leg,
      instrument: leg.instrument.replace(btcPrefix, ticker),
    };
  });
}
