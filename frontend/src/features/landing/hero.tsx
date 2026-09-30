"use client";

import { ArrowRight, CheckCircle2, CloudOff, Cpu, Languages, ScanLine } from "lucide-react";
import { AnimatePresence, motion, useScroll, useTransform } from "motion/react";
import { useEffect, useRef, useState } from "react";

import { BlightLeaf, FieldContours } from "@/components/brand/illustrations";
import { Badge } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/providers/language-provider";

const EASE = [0.22, 1, 0.36, 1] as const;

function Words({ text, delay = 0, className }: { text: string; delay?: number; className?: string }) {
  return (
    <span className={className}>
      {text.split(" ").map((w, i) => (
        <motion.span
          key={`${w}-${i}`}
          className="inline-block"
          initial={{ opacity: 0, y: "0.4em", filter: "blur(8px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 0.7, ease: EASE, delay: delay + i * 0.06 }}
        >
          {w}&nbsp;
        </motion.span>
      ))}
    </span>
  );
}

function DemoCard() {
  const { t, n } = useI18n();
  const [phase, setPhase] = useState<"scan" | "result">("scan");

  useEffect(() => {
    const id = setTimeout(() => setPhase((p) => (p === "scan" ? "result" : "scan")), phase === "scan" ? 2600 : 4200);
    return () => clearTimeout(id);
  }, [phase]);

  return (
    <div className="relative w-full max-w-sm">
      <div className="absolute -inset-6 -z-10 rounded-[2.5rem] bg-gradient-to-br from-leaf-100/70 via-transparent to-ochre-100/60 blur-2xl" />
      <motion.div
        initial={{ opacity: 0, y: 30, rotate: 2 }}
        animate={{ opacity: 1, y: 0, rotate: 0 }}
        transition={{ duration: 1, ease: EASE, delay: 0.5 }}
        className="rounded-[1.75rem] border border-line bg-surface p-3 shadow-[var(--shadow-lift)]"
      >
        <div className="relative aspect-square overflow-hidden rounded-2xl bg-gradient-to-b from-[#eef2e6] to-[#e2e8d6]">
          <div className="dotted-bg absolute inset-0 opacity-50" />
          <motion.div className="absolute inset-6 animate-sway" style={{ transformOrigin: "50% 95%" }}>
            <BlightLeaf key={phase} />
          </motion.div>
          {/* corner brackets */}
          {["top-3 left-3 border-t-2 border-l-2 rounded-tl-lg", "top-3 right-3 border-t-2 border-r-2 rounded-tr-lg", "bottom-3 left-3 border-b-2 border-l-2 rounded-bl-lg", "bottom-3 right-3 border-b-2 border-r-2 rounded-br-lg"].map((c) => (
            <span key={c} className={`absolute size-6 border-paper/90 ${c}`} />
          ))}
          <AnimatePresence>
            {phase === "scan" && (
              <motion.div exit={{ opacity: 0 }} className="absolute inset-x-0 top-0 h-full">
                <div className="h-[10%] w-full animate-scan bg-gradient-to-b from-transparent via-ochre/35 to-transparent">
                  <div className="absolute bottom-1/2 h-[2px] w-full bg-ochre shadow-[0_0_14px_var(--ochre)]" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div className="absolute top-3 left-1/2 -translate-x-1/2">
            <AnimatePresence mode="wait">
              <motion.div
                key={phase}
                initial={{ opacity: 0, y: -8, filter: "blur(4px)" }}
                animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                exit={{ opacity: 0, y: 8, filter: "blur(4px)" }}
              >
                {phase === "scan" ? (
                  <Badge tone="ink" className="gap-1.5 py-1"><ScanLine className="animate-pulse" />{t("hero.card.scanning")}</Badge>
                ) : (
                  <Badge tone="leaf" className="border-leaf-100 bg-surface py-1"><CloudOff />{t("hero.card.route")}</Badge>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        <div className="min-h-[7.5rem] px-2 pt-4 pb-2">
          <AnimatePresence mode="wait">
            {phase === "scan" ? (
              <motion.div key="s" exit={{ opacity: 0 }} className="space-y-2.5 pt-1">
                <div className="skeleton h-5 w-2/3" />
                <div className="skeleton h-3.5 w-full" />
                <div className="skeleton h-3.5 w-4/5" />
              </motion.div>
            ) : (
              <motion.div key="r" initial="h" animate="s" variants={{ s: { transition: { staggerChildren: 0.09 } } }}>
                <motion.div variants={{ h: { opacity: 0, y: 8 }, s: { opacity: 1, y: 0 } }} className="flex items-center justify-between gap-3">
                  <p className="font-display text-xl font-semibold text-ink">{t("hero.card.result")}</p>
                  <span className="font-display text-xl font-semibold text-sage tabular-nums">{n("92%")}</span>
                </motion.div>
                <motion.div variants={{ h: { scaleX: 0 }, s: { scaleX: 1 } }} className="mt-2 h-1.5 origin-left overflow-hidden rounded-full bg-paper-3">
                  <div className="h-full w-[92%] rounded-full bg-sage" />
                </motion.div>
                <motion.p variants={{ h: { opacity: 0, y: 8 }, s: { opacity: 1, y: 0 } }} className="mt-3 flex gap-2 text-sm leading-snug text-ink-2">
                  <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-leaf" />
                  {t("hero.card.action")}
                </motion.p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1.3, duration: 0.7, ease: EASE }}
        className="absolute top-16 -left-10 hidden animate-float rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink-2 shadow-[var(--shadow-soft)] sm:flex sm:items-center sm:gap-2"
      >
        <Cpu className="size-4 text-leaf" /> ViT · MobileNetV2
      </motion.div>
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1.5, duration: 0.7, ease: EASE }}
        className="absolute -right-8 bottom-40 hidden animate-float rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink-2 shadow-[var(--shadow-soft)] [animation-delay:1.5s] sm:flex sm:items-center sm:gap-2"
      >
        <Languages className="size-4 text-ochre" /> हिंदी · English
      </motion.div>
    </div>
  );
}

export function Hero() {
  const { t, n } = useI18n();
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [0, 80]);
  const fade = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  const stats = [
    { icon: Cpu, value: n("28"), label: t("hero.stat1") },
    { icon: ScanLine, value: n("75%"), label: t("hero.stat2") },
    { icon: Languages, value: n("2"), label: t("hero.stat3") },
  ];

  return (
    <section ref={ref} className="relative overflow-hidden px-4 pt-10 pb-20 sm:px-6 lg:pt-16 lg:pb-28">
      <div className="pointer-events-none absolute inset-0 -z-10 [mask-image:linear-gradient(to_bottom,black,transparent_85%)]">
        <FieldContours />
      </div>
      <motion.div style={{ y, opacity: fade }} className="mx-auto grid max-w-6xl items-center gap-14 lg:grid-cols-[1.15fr_1fr]">
        <div>
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <Badge tone="ochre" className="py-1">
              <span className="size-1.5 rounded-full bg-ochre" />
              {t("hero.eyebrow")}
            </Badge>
          </motion.div>
          <h1 className="mt-6 text-[2.6rem] leading-[1.05] font-medium sm:text-6xl lg:text-[4.2rem]">
            <Words text={t("hero.title1")} delay={0.15} />
            <br />
            <Words text={t("hero.title2")} delay={0.45} className="text-leaf italic" />
          </h1>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.7, ease: EASE }}
            className="mt-6 max-w-xl text-lg leading-relaxed text-ink-2"
          >
            {t("hero.subtitle")}
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.95, duration: 0.7, ease: EASE }}
            className="mt-9 flex flex-wrap items-center gap-3"
          >
            <Button href="/login?mode=signup" size="lg" className="group">
              {t("hero.cta")}
              <ArrowRight className="transition-transform duration-300 group-hover:translate-x-1" />
            </Button>
            <Button href="#how" variant="outline" size="lg">{t("hero.secondary")}</Button>
          </motion.div>
          <motion.dl
            initial="h"
            animate="s"
            variants={{ s: { transition: { staggerChildren: 0.1, delayChildren: 1.15 } } }}
            className="mt-12 grid max-w-md grid-cols-3 gap-4 border-t border-line pt-6"
          >
            {stats.map((s, i) => (
              <motion.div key={i} variants={{ h: { opacity: 0, y: 10 }, s: { opacity: 1, y: 0 } }}>
                <dt className="sr-only">{s.label}</dt>
                <dd className="font-display text-3xl font-semibold text-ink">{s.value}</dd>
                <dd className="mt-1 flex items-center gap-1.5 text-xs font-medium text-ink-3">
                  <s.icon className="size-3.5" /> {s.label}
                </dd>
              </motion.div>
            ))}
          </motion.dl>
        </div>
        <div className="flex justify-center lg:justify-end">
          <DemoCard />
        </div>
      </motion.div>
    </section>
  );
}
