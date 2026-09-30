"use client";

import { Search, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useMemo, useState } from "react";

import { EmptyState, ErrorState } from "@/components/feedback/empty-state";
import { DynamicScrollIslandTOC, type TOCItem } from "@/components/jyotirmoydas/dynamic-scroll-island-toc";
import { Button } from "@/components/ui/button";
import { formatDate, healthOf, parseDbDate } from "@/core/format";
import type { HistoryItem } from "@/core/types";
import { useHistory } from "@/features/farm/queries";
import { useI18n } from "@/providers/language-provider";

import { HistoryCard, HistoryCardSkeleton } from "./history-card";

type Filter = "crop" | "livestock" | "healthy" | "attention" | "cloud";

const MATCH: Record<Filter, (i: HistoryItem) => boolean> = {
  crop: (i) => i.domain === "crop",
  livestock: (i) => i.domain === "livestock",
  healthy: (i) => healthOf(i.condition, i.confidence) === "healthy",
  attention: (i) => healthOf(i.condition, i.confidence) !== "healthy",
  cloud: (i) => i.route === "cloud",
};

export function HistoryView() {
  const { t, lang, n, cond, text } = useI18n();
  const history = useHistory();
  const [query, setQuery] = useState("");

  const filters: TOCItem[] = [
    { name: t("hist.all") },
    { name: t("hist.crops"), value: "crop" },
    { name: t("hist.livestock"), value: "livestock" },
    { name: t("hist.healthy"), value: "healthy" },
    { name: t("hist.attention"), value: "attention" },
    { name: t("hist.cloud"), value: "cloud" },
  ];
  const [activeValue, setActiveValue] = useState<string | undefined>(undefined);
  const active = filters.find((f) => f.value === activeValue) ?? filters[0];

  const items = useMemo(() => {
    let rows = history.data ?? [];
    if (activeValue) rows = rows.filter(MATCH[activeValue as Filter]);
    const q = query.trim().toLowerCase();
    if (q) rows = rows.filter((r) => [r.condition, r.summary, cond(r.condition), text(r.summary)].some((f) => f.toLowerCase().includes(q)));
    return rows;
  }, [history.data, activeValue, query, cond, text]);

  // Group by month for a journal-like timeline.
  const groups = useMemo(() => {
    const map = new Map<string, HistoryItem[]>();
    for (const it of items) {
      const d = parseDbDate(it.created_at);
      const key = `${d.getFullYear()}-${d.getMonth()}`;
      map.set(key, [...(map.get(key) ?? []), it]);
    }
    return [...map.values()];
  }, [items]);

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-medium sm:text-5xl">{t("hist.title")}</h1>
          <p className="mt-2 text-ink-2">{t("hist.subtitle")}</p>
        </div>
        {history.data && (
          <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="font-display text-lg text-ink-3 italic">
            {items.length === 1 ? t("hist.countOne") : t("hist.count", { n: items.length })}
          </motion.span>
        )}
      </div>

      <div className="sticky top-20 z-20 mt-6 flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
        <DynamicScrollIslandTOC
          data={filters}
          value={active}
          setValue={(v) => setActiveValue(v.value)}
          layoutPrefix="history"
          formatProgress={(p) => n(`${p}%`)}
        />
        <label className="relative w-full sm:w-72">
          <Search className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-ink-3" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("hist.search")}
            className="h-10 w-full rounded-full border border-line bg-surface/90 pr-9 pl-10 text-sm text-ink shadow-[var(--shadow-soft)] backdrop-blur outline-none transition-[border-color,box-shadow] placeholder:text-ink-3 focus:border-leaf focus:shadow-[0_0_0_4px_var(--leaf-50)]"
          />
          {query && (
            <button onClick={() => setQuery("")} aria-label="Clear" className="absolute top-1/2 right-2.5 -translate-y-1/2 rounded-full p-1 text-ink-3 hover:bg-paper-2">
              <X className="size-3.5" />
            </button>
          )}
        </label>
      </div>

      <div className="mt-8">
        {history.isPending ? (
          <div className="space-y-3">{[0, 1, 2, 3].map((i) => <HistoryCardSkeleton key={i} />)}</div>
        ) : history.isError ? (
          <ErrorState message={text((history.error as Error).message)} onRetry={() => history.refetch()} retryLabel={t("common.retry")} />
        ) : !history.data?.length ? (
          <EmptyState title={t("hist.empty")} body={t("hist.emptyBody")} action={<Button href="/diagnose">{t("dash.newCheck")}</Button>} />
        ) : (
          <AnimatePresence mode="popLayout">
            <motion.div
              key={`${activeValue ?? "all"}-${query}`}
              initial={{ opacity: 0.4, filter: "blur(10px)", maskPosition: "0% 150%" }}
              animate={{ opacity: 1, filter: "blur(0px)", maskPosition: "0% 0%" }}
              exit={{ opacity: 0, filter: "blur(10px)" }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="[mask-image:linear-gradient(to_bottom,black_0%,black_50%,transparent_100%)] [mask-size:100%_300%] [mask-repeat:no-repeat]"
            >
              {groups.length === 0 ? (
                <EmptyState title={t("hist.emptyFilter")} />
              ) : (
                <div className="space-y-8">
                  {groups.map((g) => (
                    <section key={g[0].id}>
                      <h2 className="mb-3 flex items-center gap-3 font-display text-lg font-medium text-ink-2 italic">
                        {n(formatDate(g[0].created_at, lang, { month: "long", year: "numeric" }))}
                        <span className="h-px flex-1 bg-line" />
                      </h2>
                      <div className="space-y-3">
                        {g.map((item, i) => (
                          <motion.div key={item.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i, 8) * 0.04 }}>
                            <HistoryCard item={item} />
                          </motion.div>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
