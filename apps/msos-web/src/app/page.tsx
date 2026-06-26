import { FeaturesRow } from "@/components/FeaturesRow";
import { HeroSection } from "@/components/HeroSection";
import { ProductWindow } from "@/components/ProductWindow";
import { PublicNav } from "@/components/PublicNav";

export default function HomePage() {
  return (
    <div className="page">
      <PublicNav />
      <main className="home-main" data-self-serve-entry="homepage">
        <section className="hero" aria-label="Introduction">
          <HeroSection />
          <ProductWindow />
        </section>
        <FeaturesRow />
      </main>
    </div>
  );
}
