/** Research-beta CTA — mirrors `src/viz/signup_cta.research_offer_cta` (public demo only). */

export const DEFAULT_RESEARCH_OFFER_LABEL = "Request research beta access";

export const RESEARCH_OFFER_BLURB =
  "Research beta (v0): BTC options market-structure readouts and anomaly inspection — " +
  "decision support only, not investment advice or promised returns.";

export type ResearchOfferCta = {
  url: string;
  label: string;
  blurb: string;
};

function allowedOfferUrl(url: string): boolean {
  const lower = url.toLowerCase();
  return lower.startsWith("https://") || lower.startsWith("mailto:");
}

export function resolveResearchOfferCta(
  env: NodeJS.ProcessEnv = process.env,
): ResearchOfferCta | null {
  const url = (env.PPE_RESEARCH_OFFER_URL ?? "").trim();
  if (!url || !allowedOfferUrl(url)) {
    return null;
  }
  const label = (env.PPE_RESEARCH_OFFER_LABEL ?? "").trim() || DEFAULT_RESEARCH_OFFER_LABEL;
  return { url, label, blurb: RESEARCH_OFFER_BLURB };
}
