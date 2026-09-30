"use client";

import { Beef, CalendarDays, ChevronLeft, ChevronRight, Cloud, Cpu, MessageSquareQuote, Sprout } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { Badge, Card } from "@/components/ui/card";
import { healthOf, parseDbDate } from "@/core/format";
import type { HistoryItem } from "@/core/types";
import { Thumb } from "@/features/history/history-card";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

const dayKey = (d: Date) => `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
const HEALTH_DOT = { healthy: "bg-sage", watch: "bg-amber", disease: "bg-brick" } as const;

/** Month grid of the farmer's checks; tapping a day lists what was submitted that day. */
export function FarmCalendar({
  items, loading, hrefFor = (id) => `/history/${id}`, imageUrlFor,
}: {
  items: HistoryItem[];
  loading?: boolean;
  hrefFor?: (id: number) => string;
  imageUrlFor?: (id: number) => string;
}) {
  const { t, n, lang, cond, pct } = useI18n();
  const locale = lang === "hi" ? "hi-IN" : "en-IN";
  const today = new Date();
  const [month, setMonth] = useState(() => new Date(today.getFullYear(), today.getMonth(), 1));
  const [selected, setSelected] = useState<string>(dayKey(today));

  const byDay = useMemo(() => {
    const map = new Map<string, HistoryItem[]>();
    for (const it of items) {
      const k = dayKey(parseDbDate(it.created_at));
      map.set(k, [...(map.get(k) ?? []), it]);
    }
    return map;
  }, [items]);

  // Monday-first grid covering the whole month.
  const cells = useMemo(() => {
    const first = new Date(month);
    const offset = (first.getDay() + 6) % 7;
    const days = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
    return [...Array(offset).fill(null), ...Array.from({ length: days }, (_, i) => new Date(month.getFullYear(), month.getMonth(), i + 1))];
  }, [month]);

  const weekdays = useMemo(
    () => Array.from({ length: 7 }, (_, i) => new Date(2024, 0, 1 + i).toLocaleDateString(locale, { weekday: "narrow" })),
    [locale],
  );
  const monthChecks = items.filter((it) => {
    const d = parseDbDate(it.created_at);
    return d.getFullYear() === month.getFullYear() && d.getMonth() === month.getMonth();
  }).length;

  const shift = (delta: number) => setMonth((m) => new Date(m.getFullYear(), m.getMonth() + delta, 1));
  const isFutureMonth = month.getFullYear() * 12 + month.getMonth() >= today.getFullYear() * 12 + today.getMonth();
  const dayItems = byDay.get(selected) ?? [];
  const [sy, sm, sd] = selected.split("-").map(Number);
  const selectedLabel = new Date(sy, sm, sd).toLocaleDateString(locale, { weekday: "long", day: "numeric", month: "long" });

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="font-display text-xl font-semibold text-ink capitalize">
            {n(month.toLocaleDateString(locale, { month: "long", year: "numeric" }))}
          </p>
          <p className="text-xs font-medium text-ink-3">{t("cal.monthCount", { n: monthChecks })}</p>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              setMonth(new Date(today.getFullYear(), today.getMonth(), 1));
              setSelected(dayKey(today));
            }}
            className="h-8 rounded-full border border-line px-3 text-xs font-bold text-ink-2 transition-colors hover:border-leaf/40 hover:text-leaf"
          >
            {t("cal.today")}
          </button>
          <button onClick={() => shift(-1)} aria-label={t("cal.prev")} className="flex size-8 items-center justify-center rounded-full text-ink-2 transition-colors hover:bg-paper-2">
            <ChevronLeft className="size-4" />
          </button>
          <button
            onClick={() => shift(1)}
            disabled={isFutureMonth}
            aria-label={t("cal.next")}
            className="flex size-8 items-center justify-center rounded-full text-ink-2 transition-colors hover:bg-paper-2 disabled:opacity-30"
          >
            <ChevronRight className="size-4" />
          </button>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-7 gap-1 text-center">
        {weekdays.map((w, i) => (
          <span key={i} className="pb-1 text-[0.7rem] font-bold text-ink-3">{w}</span>
        ))}
        {cells.map((d, i) => {
          if (!d) return <span key={`e${i}`} />;
          const k = dayKey(d);
          const checks = byDay.get(k) ?? [];
          const isToday = k === dayKey(today);
          const isSel = k === selected;
          const future = d > today;
          return (
            <button
              key={k}
              onClick={() => setSelected(k)}
              disabled={future}
              aria-pressed={isSel}
              aria-label={`${d.toLocaleDateString(locale, { day: "numeric", month: "long" })}${checks.length ? ` · ${t("cal.checks", { n: checks.length })}` : ""}`}
              className={cn(
                "relative flex h-11 flex-col items-center justify-center rounded-xl sm:h-12 text-sm font-semibold tabular-nums transition-colors",
                isSel ? "text-paper" : checks.length ? "text-ink hover:bg-leaf-50" : "text-ink-2 hover:bg-paper-2",
                isToday && !isSel && "ring-[1.5px] ring-leaf ring-inset",
                future && "opacity-35",
              )}
            >
              {isSel && <motion.span layoutId="cal-selected" className="absolute inset-0 -z-0 rounded-xl bg-leaf" transition={{ type: "spring", stiffness: 420, damping: 34 }} />}
              <span className="relative">{n(d.getDate())}</span>
              {checks.length > 0 && (
                <span className="relative mt-0.5 flex gap-0.5">
                  {checks.slice(0, 3).map((c) => (
                    <span key={c.id} className={cn("size-1.5 rounded-full", isSel ? "bg-paper" : HEALTH_DOT[healthOf(c.condition, c.confidence)])} />
                  ))}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="mt-4 flex flex-wrap gap-3 text-[0.7rem] font-semibold text-ink-3">
        <span className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-sage" />{t("hist.healthy")}</span>
        <span className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-amber" />{t("cal.watch")}</span>
        <span className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-brick" />{t("hist.attention")}</span>
      </div>

      <div className="mt-5 border-t border-line pt-5">
        <p className="flex items-center gap-2 text-sm font-bold text-ink">
          <CalendarDays className="size-4 text-leaf" /> {n(selectedLabel)}
        </p>
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={selected}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2 }}
            className="mt-3 space-y-2.5"
          >
            {loading ? (
              <div className="skeleton h-16 w-full rounded-xl" />
            ) : dayItems.length === 0 ? (
              <p className="rounded-xl bg-paper-2 px-4 py-3 text-sm text-ink-3">{t("cal.empty")}</p>
            ) : (
              dayItems.map((it) => {
                const health = healthOf(it.condition, it.confidence);
                return (
                  <Link
                    key={it.id}
                    href={hrefFor(it.id)}
                    className="group flex gap-3 rounded-xl border border-line p-2.5 transition-colors hover:border-leaf/40 hover:bg-paper"
                  >
                    <Thumb item={it} src={it.has_image && imageUrlFor ? imageUrlFor(it.id) : undefined} className="size-14" />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <p className="truncate font-semibold text-ink first-letter:uppercase">{cond(it.condition)}</p>
                        <span className="shrink-0 text-xs font-bold text-ink-3 tabular-nums">
                          {n(parseDbDate(it.created_at).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit", hour12: lang !== "hi" }))}
                        </span>
                      </div>
                      <div className="mt-1 flex flex-wrap items-center gap-1.5">
                        <span className={cn("size-2 rounded-full", HEALTH_DOT[health])} />
                        <Badge>{it.domain === "crop" ? <Sprout /> : <Beef />}{it.domain === "crop" ? t("common.crop") : t("common.livestock")}</Badge>
                        <Badge tone={it.route === "cloud" ? "ochre" : "neutral"}>
                          {it.route === "cloud" ? <Cloud /> : <Cpu />}
                          {pct(it.confidence)}
                        </Badge>
                      </div>
                      <p className="mt-1.5 flex gap-1.5 text-xs leading-snug text-ink-3">
                        <MessageSquareQuote className="mt-px size-3.5 shrink-0" />
                        <span className="line-clamp-2 italic">{it.farmer_text ? `“${it.farmer_text}”` : t("cal.photoOnly")}</span>
                      </p>
                    </div>
                  </Link>
                );
              })
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </Card>
  );
}
