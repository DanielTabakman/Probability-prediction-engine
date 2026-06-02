import { FeaturesRow } from "@/components/FeaturesRow";
import { HeroSection } from "@/components/HeroSection";
import { ProductWindow } from "@/components/ProductWindow";
import { PublicNav } from "@/components/PublicNav";

export default function HomePage() {
  return (
    <div className="page">
      <PublicNav />
      <main className="hero">
        <HeroSection />
        <ProductWindow />
      </main>
      <FeaturesRow />
    </div>
  );
}
