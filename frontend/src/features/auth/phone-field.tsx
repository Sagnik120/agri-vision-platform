"use client";

import { Phone } from "lucide-react";

import { Label } from "@/components/ui/field";
import { useI18n } from "@/providers/language-provider";

export const digitsOnly = (v: string) => v.replace(/\D/g, "").slice(0, 10);
export const isValidPhone = (v: string) => /^[6-9]\d{9}$/.test(v);

/** +91 mobile number input, displayed as "98765 43210". */
export function PhoneField({ value, onChange, autoFocus, disabled }: { value: string; onChange: (v: string) => void; autoFocus?: boolean; disabled?: boolean }) {
  const { t } = useI18n();
  const shown = value.length > 5 ? `${value.slice(0, 5)} ${value.slice(5)}` : value;
  return (
    <div>
      <Label htmlFor="phone">{t("auth.phone")}</Label>
      <div className="group flex h-14 items-center rounded-xl border-[1.5px] border-line-2 bg-surface transition-[border-color,box-shadow] duration-200 focus-within:border-leaf focus-within:shadow-[0_0_0_4px_var(--leaf-50)]">
        <span className="flex h-full items-center gap-2 border-r border-line pr-3 pl-4 text-sm font-bold text-ink-2">
          <Phone className="size-4 text-ink-3 transition-colors group-focus-within:text-leaf" />
          +91
        </span>
        <input
          id="phone"
          type="tel"
          inputMode="numeric"
          autoComplete="tel-national"
          placeholder="98765 43210"
          value={shown}
          onChange={(e) => onChange(digitsOnly(e.target.value))}
          autoFocus={autoFocus}
          disabled={disabled}
          className="h-full min-w-0 flex-1 bg-transparent px-3 font-display text-xl tracking-wider text-ink outline-none placeholder:text-ink-3/40"
        />
        {isValidPhone(value) && (
          <span className="mr-4 flex size-5 items-center justify-center rounded-full bg-sage text-white animate-in zoom-in">
            <svg viewBox="0 0 12 12" className="size-3"><path d="M2.5 6.2l2.2 2.2 4.8-4.9" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </span>
        )}
      </div>
    </div>
  );
}
