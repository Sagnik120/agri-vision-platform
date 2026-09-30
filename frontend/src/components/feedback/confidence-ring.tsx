"use client";

import { animate, motion, useMotionValue, useTransform } from "motion/react";
import { useEffect } from "react";

import { confidenceTone } from "@/core/format";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

const TONE = { healthy: "var(--sage)", watch: "var(--amber)", disease: "var(--brick)" };

/** Animated ring + counting percentage, coloured by confidence band. */
export function ConfidenceRing({ value, size = 112, label, className }: { value: number; size?: number; label?: string; className?: string }) {
  const r = 42;
  const c = 2 * Math.PI * r;
  const { pct } = useI18n();
  const mv = useMotionValue(0);
  const text = useTransform(mv, (v) => pct(v));
  const offset = useTransform(mv, (v) => c * (1 - v));

  useEffect(() => {
    const ctl = animate(mv, Math.max(0, Math.min(1, value)), { duration: 1.3, ease: [0.22, 1, 0.36, 1], delay: 0.2 });
    return () => ctl.stop();
  }, [value, mv]);

  const color = TONE[confidenceTone(value)];

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)} style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100" className="absolute inset-0 -rotate-90">
        <circle cx="50" cy="50" r={r} fill="none" stroke="var(--paper-3)" strokeWidth="7" />
        <motion.circle
          cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="7" strokeLinecap="round"
          strokeDasharray={c} style={{ strokeDashoffset: offset }}
        />
      </svg>
      <div className="text-center">
        <motion.div className="font-display text-2xl leading-none font-semibold text-ink tabular-nums">{text}</motion.div>
        {label && <div className="mt-1 text-[0.65rem] font-semibold tracking-[0.14em] text-ink-3 uppercase">{label}</div>}
      </div>
    </div>
  );
}
