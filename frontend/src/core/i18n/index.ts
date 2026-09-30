import { en, type MessageKey } from "./en";
import { hi } from "./hi";

export type Lang = "en" | "hi";
export type { MessageKey };

export const LANGS: Lang[] = ["en", "hi"];
export const dictionaries: Record<Lang, Record<MessageKey, string>> = { en, hi };

const DEVANAGARI_DIGITS = "०१२३४५६७८९";

/**
 * Hindi uses Devanagari numerals. Digits glued to Latin letters (model names like
 * "MobileNetV2", "EfficientNet-B3") and phone numbers stay as they are.
 */
export function localizeDigits(s: string, lang: Lang) {
  if (lang !== "hi") return s;
  return s.replace(/(?<![A-Za-z\d+-])\d+(?:[.,]\d+)*(?![A-Za-z])/g, (m) =>
    m.length >= 10 ? m : m.replace(/\d/g, (d) => DEVANAGARI_DIGITS[Number(d)]),
  );
}

export function translate(lang: Lang, key: MessageKey, vars?: Record<string, string | number>) {
  let s: string = dictionaries[lang][key] ?? en[key] ?? key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, String(v));
  return localizeDigits(s, lang);
}
