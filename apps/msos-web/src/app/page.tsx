import { FeaturesRow } from "@/components/FeaturesRow";
import { HeroSection } from "@/components/HeroSection";
import { ProductWindow } from "@/components/ProductWindow";
import { PublicNav } from "@/components/PublicNav";
import { resolveResearchOfferCta } from "@/lib/researchOfferCta";

export default function HomePage() {
  const researchOffer = resolveResearchOfferCta();

  return (
    <div className="page">
      <PublicNav researchOffer={researchOffer} />
      <main className="hero">
        <HeroSection researchOffer={researchOffer} />
        <ProductWindow />
      </main>
      <FeaturesRow />
    </div>
  );
}
