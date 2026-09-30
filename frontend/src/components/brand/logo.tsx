"use client";

import { motion } from "motion/react";

import { cn } from "@/lib/utils";

/** Leaf outline + midrib, with an "iris" at its heart: a leaf that sees. */
const LEAF = "M24 4C12 10 6 20 7.5 31.5C8.6 39.6 15 44 24 44C33 44 39.4 39.6 40.5 31.5C42 20 36 10 24 4Z";
const RIB = "M24 12V44";
const VEIN_L = "M24 25L15.5 18.5M24 33L13 26.5";
const VEIN_R = "M24 25L32.5 18.5M24 33L35 26.5";

export function LogoMark({ className, animated = false }: { className?: string; animated?: boolean }) {
  const draw = (delay: number, duration = 0.9) =>
    animated
      ? {
          initial: { pathLength: 0, opacity: 0 },
          animate: { pathLength: 1, opacity: 1 },
          transition: { pathLength: { delay, duration, ease: [0.65, 0, 0.35, 1] as const }, opacity: { delay, duration: 0.2 } },
        }
      : {};
  const pop = (delay: number) =>
    animated
      ? {
          initial: { scale: 0, opacity: 0 },
          animate: { scale: 1, opacity: 1 },
          transition: { delay, type: "spring" as const, stiffness: 320, damping: 18 },
        }
      : {};

  return (
    <svg viewBox="0 0 48 48" fill="none" className={cn("size-8", className)} aria-hidden="true">
      <motion.path
        d={LEAF}
        fill="var(--leaf)"
        initial={animated ? { fillOpacity: 0 } : false}
        animate={{ fillOpacity: 1 }}
        transition={{ delay: animated ? 0.9 : 0, duration: 0.5 }}
      />
      <motion.path d={LEAF} stroke="var(--leaf)" strokeWidth="2.5" strokeLinejoin="round" {...draw(0, 1)} />
      <motion.path d={RIB} stroke="#fbfaf5" strokeWidth="2" strokeLinecap="round" opacity={0.85} {...draw(0.8, 0.5)} />
      <motion.path d={VEIN_L} stroke="#fbfaf5" strokeWidth="1.6" strokeLinecap="round" opacity={0.55} {...draw(1.0, 0.4)} />
      <motion.path d={VEIN_R} stroke="#fbfaf5" strokeWidth="1.6" strokeLinecap="round" opacity={0.55} {...draw(1.0, 0.4)} />
      <motion.circle cx="24" cy="20" r="5.2" fill="var(--ochre)" stroke="#fbfaf5" strokeWidth="1.8" style={{ transformOrigin: "24px 20px" }} {...pop(1.25)} />
      <motion.circle cx="24" cy="20" r="1.9" fill="var(--ink)" style={{ transformOrigin: "24px 20px" }} {...pop(1.4)} />
    </svg>
  );
}

export function Logo({ className, compact = false }: { className?: string; compact?: boolean }) {
  return (
    <span className={cn("group inline-flex items-center gap-2.5", className)}>
      <span className="transition-transform duration-500 ease-[var(--ease-out-soft)] group-hover:-rotate-6">
        <LogoMark />
      </span>
      {!compact && (
        <span className="font-display text-[1.35rem] leading-none font-semibold tracking-tight text-ink">
          Agri<span className="text-ochre">·</span>Vision
        </span>
      )}
    </span>
  );
}
