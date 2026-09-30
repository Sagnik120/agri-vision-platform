"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";

import { AppleHelloHindiEffect } from "@/components/jyotirmoydas/apple-hello-effect";
import { storage, useStoredValue } from "@/lib/storage";
import { useI18n } from "@/providers/language-provider";

import { LogoMark } from "./logo";

const SEEN_KEY = "agrivision.splash";

type Phase = "hello" | "logo" | "done";

/**
 * First-visit splash: "नमस्ते" is handwritten, then the logo draws itself.
 * Shown once per browser session; click anywhere to skip.
 */
export function SplashScreen() {
  const { t } = useI18n();
  const seen = useStoredValue(SEEN_KEY, "session");
  const [phase, setPhase] = useState<Phase>("hello");
  // Server render and hydration (seen === undefined) include the splash, so content never flashes first.
  const visible = seen !== "1" && phase !== "done";

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) storage.set(SEEN_KEY, "1", "session");
  }, []);

  useEffect(() => {
    document.documentElement.style.overflow = visible ? "hidden" : "";
  }, [visible]);

  useEffect(() => {
    if (phase === "logo") {
      const id = setTimeout(() => setPhase("done"), 1900);
      return () => clearTimeout(id);
    }
    if (phase === "done") storage.set(SEEN_KEY, "1", "session");
  }, [phase]);

  const exitVariants = {
    leave: (how: "wipe" | "instant") =>
      how === "wipe"
        ? { clipPath: "circle(0% at 50% 50%)", transition: { duration: 0.8, ease: [0.65, 0, 0.35, 1] as const } }
        : { opacity: 0, transition: { duration: 0 } },
  };

  return (
    // Returning visitors (splash already seen this session) get no animation at all.
    <AnimatePresence custom={phase === "done" ? "wipe" : "instant"}>
      {visible && (
        <motion.div
          key="splash"
          role="status"
          aria-label={t("splash.loading")}
          onClick={() => setPhase("done")}
          className="fixed inset-0 z-[100] flex cursor-pointer flex-col items-center justify-center bg-paper"
          variants={exitVariants}
          exit="leave"
          initial={{ clipPath: "circle(150% at 50% 50%)" }}
        >
          <div className="dotted-bg pointer-events-none absolute inset-0 opacity-60 [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />

          <div className="relative flex h-40 items-center justify-center">
            <AnimatePresence mode="wait">
              {phase === "hello" ? (
                <motion.div key="hello" exit={{ opacity: 0, filter: "blur(8px)", scale: 0.96, transition: { duration: 0.45 } }}>
                  <AppleHelloHindiEffect
                    className="h-24 text-leaf sm:h-28"
                    speed={0.85}
                    onAnimationComplete={() => setTimeout(() => setPhase("logo"), 250)}
                  />
                </motion.div>
              ) : (
                <motion.div
                  key="logo"
                  className="flex flex-col items-center gap-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <LogoMark animated className="size-20" />
                  <motion.p
                    className="font-display text-3xl font-semibold text-ink"
                    initial={{ opacity: 0, y: 10, filter: "blur(6px)" }}
                    animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                    transition={{ delay: 0.9, duration: 0.6 }}
                  >
                    Agri<span className="text-ochre">·</span>Vision
                  </motion.p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="absolute bottom-16 flex w-56 flex-col items-center gap-3">
            <div className="h-[3px] w-full overflow-hidden rounded-full bg-paper-3">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-leaf to-ochre"
                initial={{ width: "0%" }}
                animate={{ width: phase === "logo" ? "100%" : "62%" }}
                transition={{ duration: phase === "logo" ? 1.6 : 3.2, ease: "easeOut" }}
              />
            </div>
            <p className="text-xs tracking-[0.18em] text-ink-3 uppercase">{t("splash.loading")}</p>
          </div>

          <button
            type="button"
            onClick={() => setPhase("done")}
            className="absolute top-6 right-6 rounded-full px-3 py-1.5 text-xs font-semibold text-ink-3 transition-colors hover:bg-paper-2 hover:text-ink"
          >
            {t("splash.skip")}
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
