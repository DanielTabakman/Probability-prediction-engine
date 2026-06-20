/** Research beta CTA — mirrors `src/viz/signup_cta.research_offer_cta` (display only). */

const DEFAULT_RESEARCH_OFFER_LABEL = "Request research beta access";

export type ResearchOfferCta = {
  url: string;
  label: string;
};

function allowedOfferUrl(url: string): boolean {
  const lower = url.toLowerCase();
  return lower.startsWith("https://") || lower.startsWith("mailto:");
}

/** Returns CTA when NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL is https:// or mailto:. */
export function resolveResearchOfferCta(): ResearchOfferCta | null {
  const raw = (process.env.NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL ?? "").trim().replace(/^["']|["']$/g, "");
  if (!raw || !allowedOfferUrl(raw)) {
    return null;
  }
  const labelRaw = (process.env.NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL ?? "").trim().replace(/^["']|["']$/g, "");
  const label = labelRaw || DEFAULT_RESEARCH_OFFER_LABEL;
  return { url: raw, label };
}
