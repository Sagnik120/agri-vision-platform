"use client";

import { ArrowLeft, Beef, CalendarClock, ChevronRight, ListChecks, MapPin, Search, Sprout, TriangleAlert, UserRound, Users } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { ErrorState } from "@/components/feedback/empty-state";
import { Card } from "@/components/ui/card";
import { formatDate, timeAgo } from "@/core/format";
import { FarmCalendar } from "@/features/dashboard/farm-calendar";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import { adminApi, useAdminFarmer, useAdminFarmers } from "./api";
import { ChecksTable } from "./checks-table";

type Sort = "recent" | "checks" | "attention" | "name";

export function FarmersView() {
  const { t, n, lang, region } = useI18n();
  const q = useAdminFarmers();
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<Sort>("recent");

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const list = (q.data ?? []).filter((f) => !needle || [f.name, f.region ?? "", region(f.region ?? ""), f.phone].some((x) => x.toLowerCase().includes(needle)));
    const by: Record<Sort, (a: (typeof list)[0], b: (typeof list)[0]) => number> = {
      recent: (a, b) => (b.last_check_at ?? "").localeCompare(a.last_check_at ?? ""),
      checks: (a, b) => b.checks - a.checks,
      attention: (a, b) => b.attention - a.attention,
      name: (a, b) => a.name.localeCompare(b.name),
    };
    return [...list].sort(by[sort]);
  }, [q.data, query, sort, region]);

  const sorts: { k: Sort; label: string }[] = [
    { k: "recent", label: t("admin.sort.recent") },
    { k: "checks", label: t("admin.sort.checks") },
    { k: "attention", label: t("admin.sort.attention") },
    { k: "name", label: t("admin.sort.name") },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-medium sm:text-5xl">{t("admin.farmers.title")}</h1>
          <p className="mt-2 text-ink-2">{t("admin.farmers.subtitle")}</p>
        </div>
        {q.data && (
          <span className="inline-flex h-9 items-center gap-2 rounded-full border border-line bg-surface px-3.5 text-sm font-semibold text-ink-2">
            <Users className="size-4" /> {t("admin.farmers.count", { n: q.data.length })}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <label className="relative w-full sm:w-80">
          <Search className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-ink-3" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("admin.farmers.search")}
            className="h-10 w-full rounded-full border border-line bg-surface pr-4 pl-10 text-sm text-ink outline-none transition-[border-color,box-shadow] placeholder:text-ink-3 focus:border-leaf focus:shadow-[0_0_0_4px_var(--leaf-50)]"
          />
        </label>
        <div className="flex flex-wrap gap-1.5">
          {sorts.map((s) => (
            <button
              key={s.k}
              onClick={() => setSort(s.k)}
              className={cn("h-8 rounded-full border px-3 text-xs font-bold transition-colors", sort === s.k ? "border-ink bg-ink text-paper" : "border-line bg-surface text-ink-2 hover:border-line-2")}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {q.isError ? (
        <ErrorState message={(q.error as Error).message} onRetry={() => q.refetch()} retryLabel={t("common.retry")} />
      ) : q.isPending ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{[0, 1, 2].map((i) => <div key={i} className="skeleton h-44 rounded-2xl" />)}</div>
      ) : rows.length === 0 ? (
        <p className="rounded-xl bg-paper-2 px-4 py-6 text-center text-sm text-ink-3">{t("admin.empty")}</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {rows.map((f, i) => (
            <motion.div key={f.farm_id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i, 12) * 0.03 }}>
              <Link href={`/admin/farmers/${encodeURIComponent(f.farm_id)}`} className="group block h-full">
                <Card className="h-full p-5 transition-shadow duration-300 group-hover:shadow-[var(--shadow-lift)]">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-ochre-100 font-display text-sm font-semibold text-ochre-700">
                        {f.name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase()}
                      </span>
                      <div className="min-w-0">
                        <p className="truncate font-display text-lg font-semibold text-ink">{f.name}</p>
                        <p className="flex items-center gap-1 truncate text-xs text-ink-3">
                          <MapPin className="size-3" /> {f.region ? region(f.region) : t("admin.unknownRegion")} · {f.phone}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className="size-5 shrink-0 text-ink-3 transition-transform group-hover:translate-x-1 group-hover:text-leaf" />
                  </div>
                  <div className="mt-5 grid grid-cols-3 gap-2 text-center">
                    {[
                      { icon: ListChecks, v: f.checks, l: t("admin.col.checks"), tone: "text-ink" },
                      { icon: Sprout, v: f.crop, l: t("common.crop"), tone: "text-ink" },
                      { icon: Beef, v: f.livestock, l: t("common.livestock"), tone: "text-ink" },
                    ].map((m) => (
                      <div key={m.l} className="rounded-xl bg-paper-2 py-2">
                        <p className={cn("font-display text-xl font-semibold tabular-nums", m.tone)}>{n(m.v)}</p>
                        <p className="text-[0.7rem] font-medium text-ink-3">{m.l}</p>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 font-semibold text-ink-3">
                      <CalendarClock className="size-3.5" />
                      {f.last_check_at ? n(timeAgo(f.last_check_at, lang)) : t("admin.never")}
                    </span>
                    {f.attention > 0 && (
                      <span className="flex items-center gap-1 rounded-full bg-brick-50 px-2 py-0.5 font-bold text-brick">
                        <TriangleAlert className="size-3" /> {t("admin.kpi.cases", { n: f.attention })}
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-[0.7rem] text-ink-3">{t("admin.joined", { d: formatDate(f.created_at, lang) })}</p>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

export function FarmerDetail({ id }: { id: string }) {
  const { t, n, lang, pct, region } = useI18n();
  const q = useAdminFarmer(id);
  const f = q.data;
  const checks = f?.checks ?? [];
  const attention = checks.filter((c) => !c.healthy).length;
  const avg = checks.length ? checks.reduce((a, c) => a + c.confidence, 0) / checks.length : 0;

  return (
    <div className="space-y-6">
      <Link href="/admin/farmers" className="group inline-flex items-center gap-2 text-sm font-bold text-ink-2 transition-colors hover:text-leaf">
        <ArrowLeft className="size-4 transition-transform group-hover:-translate-x-1" /> {t("admin.backFarmers")}
      </Link>
      {q.isError ? (
        <ErrorState message={(q.error as Error).message} onRetry={() => q.refetch()} retryLabel={t("common.retry")} />
      ) : !f ? (
        <div className="skeleton h-64 rounded-2xl" />
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-4">
            <span className="flex size-16 items-center justify-center rounded-full bg-ochre-100 text-ochre-700"><UserRound className="size-7" /></span>
            <div>
              <h1 className="text-4xl font-medium">{f.name}</h1>
              <p className="mt-1 flex flex-wrap items-center gap-x-3 text-sm text-ink-3">
                <span className="flex items-center gap-1"><MapPin className="size-3.5" /> {f.region ? region(f.region) : t("admin.unknownRegion")}</span>
                <span>{f.phone}</span>
                <span>{t("admin.joined", { d: formatDate(f.created_at, lang) })}</span>
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {[
              { l: t("admin.col.checks"), v: n(checks.length) },
              { l: t("admin.kpi.attention"), v: n(attention) },
              { l: t("admin.kpi.confidence"), v: pct(avg) },
              { l: t("admin.kpi.cloud"), v: n(checks.filter((c) => c.route === "cloud").length) },
            ].map((k) => (
              <Card key={k.l} className="p-5">
                <p className="font-display text-3xl font-semibold text-ink tabular-nums">{k.v}</p>
                <p className="mt-1 text-sm font-medium text-ink-3">{k.l}</p>
              </Card>
            ))}
          </div>
          <div className="grid gap-6 lg:grid-cols-[1fr_1.4fr]">
            <section>
              <h2 className="mb-4 text-2xl font-medium">{t("cal.title")}</h2>
              <FarmCalendar items={checks} hrefFor={(cid) => `/admin/checks/${cid}`} imageUrlFor={adminApi.imageUrl} />
            </section>
            <section>
              <h2 className="mb-4 text-2xl font-medium">{t("admin.farmer.history")}</h2>
              <Card className="p-6"><ChecksTable rows={checks} compact hideFarmer /></Card>
            </section>
          </div>
        </>
      )}
    </div>
  );
}
