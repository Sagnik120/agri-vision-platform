"use client";

import { Beef, ChevronRight, Cloud, Cpu, Sprout } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";
import { useState } from "react";

import { Badge } from "@/components/ui/card";
import { diagnosisApi } from "@/core/api/endpoints";
import { healthOf, timeAgo } from "@/core/format";
import type { HistoryItem } from "@/core/types";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

const HEALTH_TONE = { healthy: "leaf", watch: "amber", disease: "brick" } as const;
const HEALTH_BAR = { healthy: "bg-sage", watch: "bg-amber", disease: "bg-brick" } as const;

export function Thumb({ item, className, src }: { item: Pick<HistoryItem, "id" | "domain" | "has_image">; className?: string; src?: string }) {
  const [failed, setFailed] = useState(false);
  const Icon = item.domain === "crop" ? Sprout : Beef;
  return (
    <div className={cn("relative shrink-0 overflow-hidden rounded-xl bg-paper-2", className)}>
      {item.has_image && !failed ? (
        // eslint-disable-next-line @next/next/no-img-element -- authenticated API image, not optimisable by next/image
        <img src={src ?? diagnosisApi.imageUrl(item.id)} alt="" loading="lazy" onError={() => setFailed(true)} className="h-full w-full object-cover" />
      ) : (
        <div className="flex h-full w-full items-center justify-center">
          <Icon className="size-6 text-ink-3" strokeWidth={1.6} />
        </div>
      )}
    </div>
  );
}

export function HistoryCard({ item }: { item: HistoryItem }) {
  const { t, lang, n, pct, cond } = useI18n();
  const health = healthOf(item.condition, item.confidence);
  const healthLabel = { healthy: t("hist.healthy"), watch: t("hist.attention"), disease: t("hist.attention") }[health];

  return (
    <Link href={`/history/${item.id}`} className="group block">
      <motion.article
        whileHover={{ y: -2 }}
        transition={{ type: "spring", stiffness: 400, damping: 28 }}
        className="relative flex items-center gap-4 overflow-hidden rounded-2xl border border-line bg-surface p-3 pr-4 shadow-[var(--shadow-soft)] transition-shadow duration-300 hover:shadow-[var(--shadow-lift)]"
      >
        <span className={cn("absolute top-0 bottom-0 left-0 w-1", HEALTH_BAR[health])} />
        <Thumb item={item} className="ml-1 size-16 transition-transform duration-500 group-hover:scale-[1.03]" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="truncate font-display text-lg leading-tight font-semibold text-ink first-letter:uppercase">{cond(item.condition)}</p>
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            <Badge tone={HEALTH_TONE[health]}>{healthLabel}</Badge>
            <Badge>{item.domain === "crop" ? t("common.crop") : t("common.livestock")}</Badge>
            <Badge tone={item.route === "cloud" ? "ochre" : "neutral"}>
              {item.route === "cloud" ? <Cloud /> : <Cpu />}
              {item.route === "cloud" ? t("res.cloud") : t("res.local")}
            </Badge>
          </div>
        </div>
        <div className="hidden text-right sm:block">
          <p className="font-display text-xl font-semibold text-ink tabular-nums">{pct(item.confidence)}</p>
          <p className="text-xs text-ink-3">{n(timeAgo(item.created_at, lang))}</p>
        </div>
        <ChevronRight className="size-5 shrink-0 text-ink-3 transition-transform duration-300 group-hover:translate-x-1 group-hover:text-leaf" />
      </motion.article>
    </Link>
  );
}

export function HistoryCardSkeleton() {
  return (
    <div className="flex items-center gap-4 rounded-2xl border border-line bg-surface p-3">
      <div className="skeleton ml-1 size-16 rounded-xl" />
      <div className="flex-1 space-y-2">
        <div className="skeleton h-5 w-1/2" />
        <div className="skeleton h-4 w-2/3" />
      </div>
    </div>
  );
}
