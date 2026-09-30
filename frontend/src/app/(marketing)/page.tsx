import { SiteHeader } from "@/components/layout/site-header";
import { Hero } from "@/features/landing/hero";
import { CoverageMarquee, CtaSection, HowSection, SiteFooter, WhySection, ZonesSection } from "@/features/landing/sections";

export default function LandingPage() {
  return (
    <>
      <SiteHeader />
      <main id="main">
        <Hero />
        <CoverageMarquee />
        <WhySection />
        <HowSection />
        <ZonesSection />
        <CtaSection />
      </main>
      <SiteFooter />
    </>
  );
}
