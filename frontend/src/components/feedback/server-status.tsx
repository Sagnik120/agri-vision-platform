"use client";

import { useQuery } from "@tanstack/react-query";
import { AnimatePresence, motion } from "motion/react";

import { metaApi } from "@/core/api/endpoints";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

export function useHealth() {
  return useQuery({ queryKey: ["health"], queryFn: metaApi.health, refetchInterval: 30_000, retry: false });
}

/** Live pill showing whether the AI server is reachable and which mode it runs in. */
export function ServerStatus({ className }: { className?: string }) {
  const { t } = useI18n();
  const { data, isError, isPending } = useHealth();

  const state = isPending ? "checking" : isError ? "offline" : data?.cloud_ready ? "cloud" : "edge";
  const label = { checking: t("status.checking"), offline: t("status.offline"), cloud: t("status.cloud"), edge: t("status.edge") }[state];
  const dot = { checking: "bg-ink-3", offline: "bg-brick", cloud: "bg-sage", edge: "bg-ochre" }[state];

  return (
    <motion.span
      layout
      className={cn(
        "inline-flex h-8 min-w-0 items-center gap-2 rounded-full border border-line bg-surface/80 px-3 text-xs font-semibold whitespace-nowrap text-ink-2 backdrop-blur",
        className,
      )}
      title={data ? `vision: ${data.expert_mode} · advisory: ${data.advisory_backend}` : undefined}
    >
      <span className={cn("relative size-2 rounded-full", dot, state !== "offline" && "animate-pulse-ring text-sage")} />
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={state}
          initial={{ opacity: 0, y: 6, filter: "blur(3px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, y: -6, filter: "blur(3px)" }}
        >
          {label}
        </motion.span>
      </AnimatePresence>
      {data?.expert_mode === "mock" && (
        <span className="hidden rounded-full bg-ochre-50 px-1.5 py-px text-[0.65rem] text-ochre-700 sm:inline">{t("status.mock")}</span>
      )}
    </motion.span>
  );
}
