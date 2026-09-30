"use client";

import { motion } from "motion/react";

import type { Lang } from "@/core/i18n";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

const OPTIONS: { value: Lang; label: string }[] = [
  { value: "en", label: "EN" },
  { value: "hi", label: "हिं" },
];

export function LanguageToggle({ className }: { className?: string }) {
  const { lang, setLang } = useI18n();
  return (
    <div role="radiogroup" aria-label="Language" className={cn("relative flex h-8 rounded-full border border-line bg-surface/80 p-0.5 backdrop-blur", className)}>
      {OPTIONS.map((o) => (
        <button
          key={o.value}
          role="radio"
          aria-checked={lang === o.value}
          onClick={() => setLang(o.value)}
          className={cn(
            "relative z-10 w-10 rounded-full text-xs font-bold transition-colors duration-300",
            lang === o.value ? "text-paper" : "text-ink-3 hover:text-ink",
          )}
        >
          {lang === o.value && (
            <motion.span
              layoutId="lang-pill"
              className="absolute inset-0 -z-10 rounded-full bg-ink"
              transition={{ type: "spring", stiffness: 420, damping: 32 }}
            />
          )}
          {o.label}
        </button>
      ))}
    </div>
  );
}
