import type { Lang } from "./i18n";

export const pct = (v: number | null | undefined) => `${Math.round((v ?? 0) * 100)}%`;

/** SQLite `datetime('now')` is UTC without a zone marker. */
export function parseDbDate(s: string) {
  return new Date(s.includes("T") ? s : `${s.replace(" ", "T")}Z`);
}

export function formatDate(s: string, lang: Lang, opts: Intl.DateTimeFormatOptions = { day: "numeric", month: "short", year: "numeric" }) {
  return parseDbDate(s).toLocaleDateString(lang === "hi" ? "hi-IN" : "en-IN", opts);
}

export function timeAgo(s: string, lang: Lang) {
  const diff = (parseDbDate(s).getTime() - Date.now()) / 1000;
  const rtf = new Intl.RelativeTimeFormat(lang === "hi" ? "hi-IN" : "en-IN", { numeric: "auto" });
  const units: [Intl.RelativeTimeFormatUnit, number][] = [
    ["year", 31536000], ["month", 2592000], ["week", 604800], ["day", 86400], ["hour", 3600], ["minute", 60],
  ];
  for (const [unit, sec] of units) if (Math.abs(diff) >= sec) return rtf.format(Math.round(diff / sec), unit);
  return rtf.format(Math.round(diff), "second");
}

export type Health = "healthy" | "watch" | "disease";

export function healthOf(condition: string, confidence: number): Health {
  if (/healthy/i.test(condition)) return "healthy";
  return confidence >= 0.75 ? "disease" : "watch";
}

export function confidenceTone(v: number): Health {
  if (v >= 0.75) return "healthy";
  if (v >= 0.5) return "watch";
  return "disease";
}

export function greetingKey(date = new Date()) {
  const h = date.getHours();
  if (h < 12) return "greet.morning" as const;
  if (h < 17) return "greet.afternoon" as const;
  return "greet.evening" as const;
}
