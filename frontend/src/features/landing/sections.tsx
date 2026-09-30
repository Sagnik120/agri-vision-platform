"use client";

import { ArrowRight, Camera, ClipboardCheck, Cloud, Cpu, Database, Languages, Layers, Microscope, ShieldCheck, WifiOff } from "lucide-react";
import { motion, useScroll, useTransform } from "motion/react";
import Link from "next/link";
import { useRef } from "react";

import AnimatedBlurTestimonials from "@/components/daddy/animated-blur-testimonials";
import { Logo } from "@/components/brand/logo";
import { Reveal, Stagger, StaggerItem } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/card";
import { useI18n } from "@/providers/language-provider";

// Straight from src/zone1_edge/knowledge/local_advisories.json
const CONDITIONS = [
  "Tomato late blight", "Potato early blight", "Maize common rust", "Wheat rust", "Rice blast", "Cotton bollworm",
  "Pepper bacterial spot", "Soybean rust", "Citrus canker", "Mango anthracnose", "Banana bunchy top", "Nitrogen deficiency",
  "Lumpy skin disease", "Foot & mouth disease", "Mastitis", "Heat stress", "Ketosis", "Newcastle disease", "Avian influenza", "PPR (goats)",
];

const CONDITIONS_HI = [
  "टमाटर का पछेती झुलसा", "आलू का अगेती झुलसा", "मक्के का सामान्य रतुआ", "गेहूँ का रतुआ", "धान का झोंका रोग", "कपास की सुंडी",
  "शिमला मिर्च का जीवाणु धब्बा", "सोयाबीन का रतुआ", "नींबू वर्गीय कैंकर", "आम का एन्थ्रेक्नोज़", "केले का गुच्छा शीर्ष रोग", "नाइट्रोजन की कमी",
  "लम्पी त्वचा रोग", "खुरपका-मुंहपका रोग", "थनैला रोग", "गर्मी का तनाव", "कीटोसिस", "रानीखेत रोग", "बर्ड फ़्लू", "पीपीआर (बकरी)",
];

function SectionHeading({ eyebrow, title, subtitle }: { eyebrow: string; title: string; subtitle?: string }) {
  return (
    <Reveal className="mx-auto max-w-2xl text-center">
      <p className="text-xs font-bold tracking-[0.2em] text-ochre-700 uppercase">{eyebrow}</p>
      <h2 className="mt-3 text-4xl leading-tight font-medium sm:text-5xl">{title}</h2>
      {subtitle && <p className="mt-4 text-lg text-ink-2">{subtitle}</p>}
    </Reveal>
  );
}

export function CoverageMarquee() {
  const { t, lang } = useI18n();
  const names = lang === "hi" ? CONDITIONS_HI : CONDITIONS;
  const row = [...names, ...names];
  return (
    <section aria-label={t("cover.title")} className="border-y border-line bg-paper-2/60 py-5">
      <p className="sr-only">{names.join(", ")}</p>
      <div className="relative overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_8%,black_92%,transparent)]" aria-hidden>
        <motion.div
          className="flex w-max gap-3"
          animate={{ x: ["0%", "-50%"] }}
          transition={{ duration: 60, ease: "linear", repeat: Infinity }}
        >
          {row.map((c, i) => (
            <span key={i} className="flex items-center gap-3 font-display text-lg whitespace-nowrap text-ink-2 italic">
              {c}
              <span className="size-1.5 rounded-full bg-ochre/60" />
            </span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

export function WhySection() {
  const { t } = useI18n();
  const items = [
    { icon: WifiOff, title: t("why.1.title"), body: t("why.1.body") },
    { icon: Languages, title: t("why.2.title"), body: t("why.2.body") },
    { icon: Layers, title: t("why.3.title"), body: t("why.3.body") },
  ];
  return (
    <section id="why" className="scroll-mt-24 px-4 py-24 sm:px-6">
      <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2">
        <div>
          <Reveal>
            <p className="text-xs font-bold tracking-[0.2em] text-ochre-700 uppercase">{t("nav.why")}</p>
            <h2 className="mt-3 text-4xl leading-tight font-medium sm:text-5xl">{t("why.title")}</h2>
            <p className="mt-4 text-lg text-ink-2">{t("why.subtitle")}</p>
          </Reveal>
        </div>
        <Reveal delay={0.1}>
          <AnimatedBlurTestimonials
            delayDuration={7}
            data={items.map((it) => ({
              label: it.title,
              avatar: { fallback: <it.icon className="size-5" /> },
              message: (
                <span className="block">
                  <span className="block font-display text-2xl leading-snug font-medium text-ink">{it.title}</span>
                  <span className="mt-3 block text-base leading-relaxed text-ink-2">{it.body}</span>
                </span>
              ),
            }))}
          />
        </Reveal>
      </div>
    </section>
  );
}

export function HowSection() {
  const { t, n } = useI18n();
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 75%", "end 55%"] });
  const line = useTransform(scrollYProgress, [0, 1], [0, 1]);

  const steps = [
    { icon: Camera, title: t("how.1.title"), body: t("how.1.body") },
    { icon: Microscope, title: t("how.2.title"), body: t("how.2.body") },
    { icon: ClipboardCheck, title: t("how.3.title"), body: t("how.3.body") },
  ];

  return (
    <section id="how" className="scroll-mt-24 bg-surface/60 px-4 py-24 sm:px-6">
      <SectionHeading eyebrow={t("nav.how")} title={t("how.title")} />
      <div ref={ref} className="relative mx-auto mt-16 max-w-5xl">
        <svg className="absolute top-8 left-[16.66%] hidden h-2 w-[66.66%] md:block" preserveAspectRatio="none" viewBox="0 0 100 2" aria-hidden>
          <line x1="0" y1="1" x2="100" y2="1" stroke="var(--line-2)" strokeWidth="2" strokeDasharray="1.5 1.5" vectorEffect="non-scaling-stroke" />
          <motion.line x1="0" y1="1" x2="100" y2="1" stroke="var(--leaf)" strokeWidth="2" style={{ pathLength: line }} vectorEffect="non-scaling-stroke" />
        </svg>
        <Stagger className="grid gap-10 md:grid-cols-3" stagger={0.15}>
          {steps.map((s, i) => (
            <StaggerItem key={i} className="relative text-center">
              <div className="relative mx-auto flex size-16 items-center justify-center rounded-2xl border border-line bg-surface shadow-[var(--shadow-soft)]">
                <s.icon className="size-7 text-leaf" strokeWidth={1.6} />
                <span className="absolute -top-2 -right-2 flex size-6 items-center justify-center rounded-full bg-ochre font-display text-xs font-bold text-ink">
                  {n(i + 1)}
                </span>
              </div>
              <h3 className="mt-6 text-2xl font-medium">{s.title}</h3>
              <p className="mx-auto mt-2 max-w-xs leading-relaxed text-ink-2">{s.body}</p>
            </StaggerItem>
          ))}
        </Stagger>
      </div>
    </section>
  );
}

export function ZonesSection() {
  const { t, n } = useI18n();
  const zones = [
    { icon: Cpu, name: t("zones.1.name"), body: t("zones.1.body"), tag: t("zones.1.tag"), tone: "leaf" as const, accent: "bg-leaf" },
    { icon: Cloud, name: t("zones.2.name"), body: t("zones.2.body"), tag: t("zones.2.tag"), tone: "ochre" as const, accent: "bg-ochre" },
    { icon: Database, name: t("zones.3.name"), body: t("zones.3.body"), tag: t("zones.3.tag"), tone: "neutral" as const, accent: "bg-ink" },
  ];
  return (
    <section id="zones" className="scroll-mt-24 px-4 py-24 sm:px-6">
      <SectionHeading eyebrow={t("nav.zones")} title={t("zones.title")} subtitle={t("zones.subtitle")} />
      <Stagger className="mx-auto mt-14 grid max-w-6xl gap-5 md:grid-cols-3" stagger={0.12}>
        {zones.map((z, i) => (
          <StaggerItem key={i}>
            <motion.article
              whileHover={{ y: -6 }}
              transition={{ type: "spring", stiffness: 300, damping: 22 }}
              className="group relative h-full overflow-hidden rounded-2xl border border-line bg-surface p-7 shadow-[var(--shadow-soft)] transition-shadow duration-500 hover:shadow-[var(--shadow-lift)]"
            >
              <span className={`absolute inset-x-0 top-0 h-1 origin-left scale-x-0 ${z.accent} transition-transform duration-500 group-hover:scale-x-100`} />
              <div className="relative z-10 flex items-center justify-between">
                <span className="flex size-12 items-center justify-center rounded-xl bg-paper-2 transition-colors duration-500 group-hover:bg-leaf-50">
                  <z.icon className="size-6 text-ink-2 transition-colors group-hover:text-leaf" strokeWidth={1.6} />
                </span>
                <Badge tone={z.tone}>{z.tag}</Badge>
              </div>
              <h3 className="relative z-10 mt-6 text-2xl font-medium">{z.name}</h3>
              <p className="relative z-10 mt-3 leading-relaxed text-ink-2">{z.body}</p>
              <span className="pointer-events-none absolute -right-3 -bottom-8 font-display text-[8rem] leading-none font-semibold text-paper-2 transition-colors duration-500 group-hover:text-leaf-50">
                {n(i + 1)}
              </span>
            </motion.article>
          </StaggerItem>
        ))}
      </Stagger>
    </section>
  );
}

export function CtaSection() {
  const { t } = useI18n();
  return (
    <section className="px-4 pb-24 sm:px-6">
      <Reveal className="relative mx-auto max-w-6xl overflow-hidden rounded-[2rem] bg-leaf px-6 py-16 text-center sm:px-16">
        <div className="pointer-events-none absolute inset-0 opacity-[0.12] [background-image:radial-gradient(circle,#fff_1px,transparent_1px)] [background-size:22px_22px]" />
        <div className="pointer-events-none absolute -top-24 -right-24 size-72 rounded-full bg-ochre/30 blur-3xl" />
        <h2 className="relative mx-auto max-w-2xl text-4xl leading-tight font-medium !text-paper sm:text-5xl">{t("cta.title")}</h2>
        <p className="relative mx-auto mt-4 max-w-lg text-lg text-paper/75">{t("cta.body")}</p>
        <div className="relative mt-9 flex justify-center">
          <Button href="/login?mode=signup" variant="accent" size="lg" className="group">
            {t("cta.button")}
            <ArrowRight className="transition-transform duration-300 group-hover:translate-x-1" />
          </Button>
        </div>
      </Reveal>
    </section>
  );
}

export function SiteFooter() {
  const { t } = useI18n();
  return (
    <footer className="border-t border-line px-4 py-10 sm:px-6">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-sm text-ink-3 sm:flex-row">
        <Logo />
        <p className="text-center">{t("footer.note")}</p>
        <Link href="/login?role=admin" className="inline-flex items-center gap-1.5 font-semibold text-ink-3 transition-colors hover:text-leaf">
          <ShieldCheck className="size-4" /> {t("footer.admin")}
        </Link>
      </div>
    </footer>
  );
}
