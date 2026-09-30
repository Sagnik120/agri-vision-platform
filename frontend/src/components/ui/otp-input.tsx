"use client";

import { motion, useAnimationControls } from "motion/react";
import { useEffect, useRef, useState } from "react";

import { cn } from "@/lib/utils";

interface OtpInputProps {
  length: number;
  value: string;
  onChange: (v: string) => void;
  onComplete?: (v: string) => void;
  /** Masks digits (for PINs). */
  secret?: boolean;
  /** Bump this number to play the "wrong code" shake. */
  errorSignal?: number;
  success?: boolean;
  disabled?: boolean;
  autoFocus?: boolean;
  label: string;
}

/**
 * Individual digit boxes backed by a single hidden input, so paste,
 * SMS autofill (autocomplete="one-time-code") and backspace all just work.
 */
export function OtpInput({ length, value, onChange, onComplete, secret, errorSignal = 0, success, disabled, autoFocus, label }: OtpInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const controls = useAnimationControls();
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    if (errorSignal > 0) controls.start({ x: [0, -10, 9, -7, 5, -2, 0], transition: { duration: 0.45 } });
  }, [errorSignal, controls]);

  useEffect(() => {
    if (autoFocus) inputRef.current?.focus();
  }, [autoFocus]);

  const handle = (raw: string) => {
    const digits = raw.replace(/\D/g, "").slice(0, length);
    onChange(digits);
    if (digits.length === length) onComplete?.(digits);
  };

  const active = Math.min(value.length, length - 1);

  return (
    <motion.div animate={controls} className="relative" onClick={() => inputRef.current?.focus()}>
      <input
        ref={inputRef}
        aria-label={label}
        value={value}
        onChange={(e) => handle(e.target.value)}
        inputMode="numeric"
        autoComplete={secret ? "off" : "one-time-code"}
        maxLength={length}
        disabled={disabled}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        className="absolute inset-0 z-10 w-full cursor-text opacity-0"
      />
      <div className="flex justify-between gap-2 sm:gap-3">
        {Array.from({ length }).map((_, i) => {
          const ch = value[i];
          const isActive = focused && i === active && value.length < length;
          return (
            <div
              key={i}
              className={cn(
                "relative flex aspect-[5/6] w-full max-w-14 items-center justify-center rounded-xl border-[1.5px] bg-surface font-display text-2xl font-semibold text-ink transition-all duration-200",
                "border-line-2",
                isActive && "border-leaf shadow-[0_0_0_4px_var(--leaf-50)]",
                ch && "border-ink-3/40 bg-paper",
                errorSignal > 0 && !success && value.length === length && "border-brick bg-brick-50",
                success && "border-sage bg-leaf-50 text-leaf",
              )}
            >
              {ch && (
                <motion.span
                  key={ch + i}
                  initial={{ y: 8, opacity: 0, scale: 0.6 }}
                  animate={{ y: 0, opacity: 1, scale: 1 }}
                  transition={{ type: "spring", stiffness: 500, damping: 26, delay: success ? i * 0.04 : 0 }}
                >
                  {secret ? <span className="block size-3 rounded-full bg-ink" /> : ch}
                </motion.span>
              )}
              {isActive && (
                <span className="absolute bottom-3 h-[2px] w-4 animate-pulse rounded-full bg-leaf" />
              )}
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
