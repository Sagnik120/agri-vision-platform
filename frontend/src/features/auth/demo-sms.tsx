"use client";

import { MessageSquareText, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";

import { useI18n } from "@/providers/language-provider";

/**
 * DEMO ONLY: shows the OTP as a phone-style SMS notification, since the
 * backend does not send real SMS in demo mode (see src/api/otp.py).
 */
export function DemoSms({ code, onUse, onClose }: { code: string | null; onUse: (c: string) => void; onClose: () => void }) {
  const { t } = useI18n();
  return (
    <AnimatePresence>
      {code && (
        <motion.div
          key={code}
          initial={{ y: -120, opacity: 0, scale: 0.95 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          exit={{ y: -120, opacity: 0, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 260, damping: 24 }}
          drag="y"
          dragConstraints={{ top: 0, bottom: 0 }}
          dragElastic={{ top: 0.6, bottom: 0.1 }}
          onDragEnd={(_, info) => info.offset.y < -40 && onClose()}
          className="fixed top-4 right-4 left-4 z-[60] mx-auto max-w-sm sm:left-auto"
          role="alert"
        >
          <div className="overflow-hidden rounded-2xl border border-white/40 bg-[#f7f5ef]/90 shadow-[0_20px_50px_-15px_rgb(31_42_36/0.45)] backdrop-blur-xl">
            <button type="button" onClick={() => onUse(code)} className="flex w-full items-start gap-3 p-3.5 text-left">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-[0.6rem] bg-sage text-white">
                <MessageSquareText className="size-5" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="flex items-center justify-between text-xs">
                  <span className="font-bold tracking-wide text-ink">{t("sms.from")}</span>
                  <span className="text-ink-3">{t("sms.now")}</span>
                </span>
                <span className="mt-0.5 block text-sm leading-snug text-ink-2">
                  <strong className="font-display text-base tracking-[0.2em] text-ink">{code}</strong> {t("sms.body")}
                </span>
                <span className="mt-1.5 inline-flex items-center gap-1 rounded-full bg-leaf-50 px-2 py-0.5 text-[0.7rem] font-semibold text-leaf">
                  {t("sms.copy")} →
                </span>
              </span>
            </button>
            <div className="flex items-center justify-between border-t border-line/70 bg-ochre-50/80 px-3.5 py-1.5">
              <span className="text-[0.7rem] font-semibold text-ochre-700">{t("sms.demo")}</span>
              <button type="button" onClick={onClose} aria-label="Dismiss" className="rounded p-0.5 text-ink-3 hover:bg-paper-3">
                <X className="size-3.5" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
