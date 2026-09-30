"use client";

import { BookOpenCheck, Check, Cloud, Database, Gauge, ImageUp, Microscope, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";

import { ShimmeringText } from "@/components/jyotirmoydas/shimmering-text";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import type { RunState, StepId } from "./use-diagnosis-run";

const ICONS: Record<StepId, typeof Check> = {
  upload: ImageUp,
  vision: Microscope,
  gate: Gauge,
  knowledge: BookOpenCheck,
  cloud: Cloud,
  save: Database,
};

export function PipelineTimeline({ state }: { state: RunState }) {
  const { t, cond, pct } = useI18n();
  const cloud = state.route === "cloud";
  const order: StepId[] = cloud ? ["upload", "vision", "gate", "knowledge", "cloud", "save"] : ["upload", "vision", "gate", "save"];

  const label = (id: StepId) => {
    const s = state.steps[id];
    if (id === "vision" && s === "done" && state.prediction) return t("stage.visionDone", { p: cond(state.prediction) });
    if (id === "gate" && s === "done" && state.confidence !== undefined)
      return t(cloud ? "stage.gateCloud" : "stage.gateLocal", { c: pct(state.confidence) });
    return t(`stage.${id}` as const);
  };

  return (
    <ol className="relative">
      <AnimatePresence initial={false}>
        {order.map((id, i) => {
          const s = state.steps[id];
          const Icon = ICONS[id];
          const last = i === order.length - 1;
          return (
            <motion.li
              key={id}
              layout
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              className="relative flex gap-4 pb-6 last:pb-0"
            >
              {!last && (
                <span className="absolute top-11 bottom-1 left-[1.3rem] w-0.5 overflow-hidden rounded-full bg-paper-3">
                  <motion.span
                    className="block w-full rounded-full bg-leaf"
                    initial={false}
                    animate={{ height: s === "done" ? "100%" : "0%" }}
                    transition={{ duration: 0.45 }}
                  />
                </span>
              )}
              <motion.span
                initial={false}
                animate={{ scale: s === "active" ? 1.06 : 1 }}
                className={cn(
                  "relative z-10 flex size-11 shrink-0 items-center justify-center rounded-2xl border transition-colors duration-500",
                  s === "done" && "border-leaf bg-leaf text-paper",
                  s === "active" && "border-leaf bg-leaf-50 text-leaf",
                  s === "error" && "border-brick bg-brick-50 text-brick",
                  s === "pending" && "border-line bg-surface text-ink-3",
                  id === "cloud" && s !== "pending" && s !== "error" && "border-ochre bg-ochre-50 text-ochre-700",
                  id === "cloud" && s === "done" && "bg-ochre text-ink",
                )}
              >
                <AnimatePresence mode="wait" initial={false}>
                  <motion.span
                    key={s}
                    initial={{ scale: 0.4, opacity: 0, rotate: -30 }}
                    animate={{ scale: 1, opacity: 1, rotate: 0 }}
                    exit={{ scale: 0.4, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 500, damping: 25 }}
                  >
                    {s === "done" ? <Check className="size-5" strokeWidth={2.6} /> : s === "error" ? <X className="size-5" /> : <Icon className="size-5" strokeWidth={1.8} />}
                  </motion.span>
                </AnimatePresence>
                {s === "active" && <span className="absolute inset-0 animate-ping rounded-2xl border-2 border-leaf/30" />}
              </motion.span>
              <div className="min-w-0 pt-2.5">
                <AnimatePresence mode="wait" initial={false}>
                  <motion.p
                    key={`${s}-${label(id)}`}
                    initial={{ opacity: 0, y: 6, filter: "blur(3px)" }}
                    animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                    exit={{ opacity: 0, y: -6, filter: "blur(3px)" }}
                    className={cn("text-[0.95rem] font-semibold first-letter:uppercase", s === "pending" ? "text-ink-3" : "text-ink")}
                  >
                    {s === "active" ? (
                      <ShimmeringText text={label(id)} duration={1.2} className="[--color:var(--ink-3)] [--shimmering-color:var(--leaf)]" />
                    ) : (
                      label(id)
                    )}
                  </motion.p>
                </AnimatePresence>
              </div>
            </motion.li>
          );
        })}
      </AnimatePresence>
    </ol>
  );
}
