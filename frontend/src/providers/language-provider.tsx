"use client";

import { createContext, useCallback, useContext, useEffect, useMemo } from "react";

import { type Lang, type MessageKey, localizeDigits, translate } from "@/core/i18n";
import { REGION_HI, conditionHi, sentenceHi } from "@/core/i18n/content-hi";
import { storage, useStoredValue } from "@/lib/storage";

interface LanguageContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: MessageKey, vars?: Record<string, string | number>) => string;
  /** Numbers/strings with digits in the active script (Devanagari for Hindi). */
  n: (v: number | string) => string;
  /** 0..1 -> "92%" in the active script. */
  pct: (v: number | null | undefined) => string;
  /** Model label / condition name from the backend. */
  cond: (label: string) => string;
  /** Known sentence from the backend (advisory knowledge base, gate reasons, …). */
  text: (s: string) => string;
  /** Indian state name. */
  region: (r: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);
const KEY = "agrivision.lang";

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const saved = useStoredValue(KEY);
  const lang: Lang = saved === "hi" ? "hi" : "en";

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((l: Lang) => storage.set(KEY, l), []);

  const value = useMemo<LanguageContextValue>(() => {
    const hi = lang === "hi";
    const n = (v: number | string) => localizeDigits(String(v), lang);
    return {
      lang,
      setLang,
      t: (key, vars) => translate(lang, key, vars),
      n,
      pct: (v) => n(`${Math.round((v ?? 0) * 100)}%`),
      cond: (label) => (hi ? (conditionHi(label) ?? label) : label),
      text: (s) => (hi && s ? localizeDigits(sentenceHi(s) ?? s, lang) : s),
      region: (r) => (hi ? (REGION_HI[r] ?? r) : r),
    };
  }, [lang, setLang]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useI18n must be used inside LanguageProvider");
  return ctx;
}
