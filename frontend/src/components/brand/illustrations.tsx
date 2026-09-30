"use client";

import { motion } from "motion/react";

import { cn } from "@/lib/utils";

/** Hand-drawn style tomato leaf with blight lesions, used in the hero demo card. */
export function BlightLeaf({ className, spots = true }: { className?: string; spots?: boolean }) {
  return (
    <svg viewBox="0 0 240 240" fill="none" className={cn("h-full w-full", className)} aria-hidden>
      <defs>
        <linearGradient id="leafFill" x1="40" y1="30" x2="200" y2="210" gradientUnits="userSpaceOnUse">
          <stop stopColor="#5b8c5a" />
          <stop offset="1" stopColor="#2f5d3a" />
        </linearGradient>
        <radialGradient id="lesion" cx="0.5" cy="0.5" r="0.5">
          <stop stopColor="#5a3a1c" />
          <stop offset="0.6" stopColor="#7a5224" />
          <stop offset="1" stopColor="#b98b3c" stopOpacity="0.2" />
        </radialGradient>
      </defs>
      <path d="M120 222 C 118 200, 117 190, 118 176" stroke="#3e4b43" strokeWidth="4" strokeLinecap="round" />
      <path
        d="M118 178 C 58 170, 26 120, 42 70 C 50 44, 80 22, 122 18 C 164 22, 196 50, 202 90 C 210 140, 176 176, 118 178 Z"
        fill="url(#leafFill)"
      />
      <path d="M118 176 C 120 130, 122 80, 122 22" stroke="#eef4ec" strokeOpacity="0.55" strokeWidth="2.5" strokeLinecap="round" />
      {[
        "M121 60 C 100 52, 82 50, 64 56", "M121 90 C 96 84, 72 86, 52 98", "M120 122 C 98 120, 78 126, 60 140",
        "M122 60 C 144 50, 164 50, 182 60", "M122 92 C 148 86, 172 90, 192 104", "M121 124 C 146 122, 166 130, 182 146",
      ].map((d) => (
        <path key={d} d={d} stroke="#eef4ec" strokeOpacity="0.3" strokeWidth="1.6" strokeLinecap="round" />
      ))}
      {spots &&
        [
          [150, 78, 13], [82, 112, 10], [158, 128, 9], [96, 70, 6], [140, 150, 6], [74, 140, 5],
        ].map(([cx, cy, r], i) => (
          <motion.circle
            key={i}
            cx={cx} cy={cy} r={r}
            fill="url(#lesion)"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.4 + i * 0.12, type: "spring", stiffness: 200, damping: 14 }}
            style={{ transformOrigin: `${cx}px ${cy}px` }}
          />
        ))}
    </svg>
  );
}

/** Thin contour lines like a field survey map — decorative background. */
export function FieldContours({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 800 600" fill="none" preserveAspectRatio="xMidYMid slice" className={cn("h-full w-full", className)} aria-hidden>
      {Array.from({ length: 11 }).map((_, i) => (
        <motion.path
          key={i}
          d={`M-40 ${120 + i * 42} C 160 ${60 + i * 44}, 300 ${200 + i * 36}, 460 ${130 + i * 40} S 720 ${80 + i * 46}, 860 ${150 + i * 40}`}
          stroke="var(--leaf)"
          strokeOpacity={0.07 + (i % 3) * 0.02}
          strokeWidth="1.2"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2.4, delay: 0.2 + i * 0.07, ease: [0.65, 0, 0.35, 1] }}
        />
      ))}
    </svg>
  );
}

/** Small sprouting seedling for empty states. */
export function Seedling({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 120" fill="none" className={cn("size-28", className)} aria-hidden>
      <ellipse cx="60" cy="100" rx="38" ry="7" fill="var(--paper-3)" />
      <motion.path
        d="M60 100 V 58" stroke="var(--leaf)" strokeWidth="3.5" strokeLinecap="round"
        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8 }}
      />
      <motion.path
        d="M60 70 C 44 70, 32 60, 30 44 C 46 42, 58 52, 60 70 Z" fill="var(--sage)"
        initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.6, type: "spring" }}
        style={{ transformOrigin: "60px 70px" }}
      />
      <motion.path
        d="M60 60 C 72 58, 86 48, 90 32 C 74 30, 62 42, 60 60 Z" fill="var(--leaf)"
        initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.8, type: "spring" }}
        style={{ transformOrigin: "60px 60px" }}
      />
    </svg>
  );
}
