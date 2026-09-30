"use client";

import { ArrowRight, Beef, CalendarDays, CheckCircle2, CloudOff, ListChecks, MapPin, ScanLine, Sprout, TriangleAlert } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";

import { EmptyState, ErrorState } from "@/components/feedback/empty-state";
import { CountUp, Stagger, StaggerItem } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { greetingKey } from "@/core/format";
import type { MessageKey } from "@/core/i18n";
import { HistoryCard, HistoryCardSkeleton } from "@/features/history/history-card";
import { useHistory, useMeta, useStats } from "@/features/farm/queries";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

import { FarmCalendar } from "./farm-calendar";
import { WeatherCard } from "./weather-card";

function StatTile({ icon: Icon, label, value, tone }: { icon: typeof ListChecks; label: string; value?: number; tone: string }) {
  const { n, lang } = useI18n();
  return (
    <Card className="group relative overflow-hidden p-5">
      <div className={`flex size-10 items-center justify-center rounded-xl ${tone} transition-transform duration-500 group-hover:rotate-[-8deg]`}>
        <Icon className="size-5" strokeWidth={1.8} />
      </div>
      <p className="mt-5 font-display text-4xl font-semibold text-ink tabular-nums">
        {value === undefined ? <span className="skeleton inline-block h-9 w-12 align-middle" /> : <CountUp key={lang} value={value} format={n} />}
      </p>
      <p className="mt-1 text-sm font-medium text-ink-3">{label}</p>
    </Card>
  );
}

export function DashboardView() {
  const { t, lang, n, region, text } = useI18n();
  const { farmer } = useSession();
  const stats = useStats();
  const history = useHistory();
  const meta = useMeta();

  const seasonLabel = (s: string) => (["kharif", "rabi", "zaid"].includes(s) ? t(`season.${s}` as MessageKey) : s);
  const firstName = farmer?.name?.split(" ")[0] ?? "";
  const today = new Date().toLocaleDateString(lang === "hi" ? "hi-IN" : "en-IN", { weekday: "long", day: "numeric", month: "long" });
  const s = stats.data;
  const cropShare = s && s.total ? (s.crop / s.total) * 100 : 50;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-ink-3">{n(today)}</p>
          <h1 className="mt-1 text-4xl font-medium sm:text-5xl">
            {t(greetingKey())}, <span className="text-leaf italic">{firstName}</span>
          </h1>
          <p className="mt-2 text-ink-2">{t("dash.subtitle")}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href="/settings" className="inline-flex h-9 items-center gap-2 rounded-full border border-line bg-surface px-3.5 text-sm font-semibold text-ink-2 transition-colors hover:border-leaf/40 hover:text-leaf">
            <MapPin className="size-4" /> {farmer?.region ? region(farmer.region) : t("dash.regionUnset")}
          </Link>
          {meta.data && (
            <span className="inline-flex h-9 items-center gap-2 rounded-full border border-line bg-surface px-3.5 text-sm font-semibold text-ink-2">
              <CalendarDays className="size-4" /> {t("dash.season")}: {seasonLabel(meta.data.current_season)}
            </span>
          )}
        </div>
      </div>

      <Link href="/diagnose" className="group block">
        <motion.div
          whileHover={{ scale: 1.005 }}
          className="relative overflow-hidden rounded-3xl bg-leaf p-7 text-paper shadow-[var(--shadow-lift)] sm:p-9"
        >
          <div className="pointer-events-none absolute inset-0 opacity-[0.1] [background-image:radial-gradient(circle,#fff_1px,transparent_1px)] [background-size:20px_20px]" />
          <div className="pointer-events-none absolute -top-20 -right-10 size-64 rounded-full bg-ochre/30 blur-3xl transition-transform duration-700 group-hover:scale-125" />
          <div className="relative flex items-center justify-between gap-6">
            <div>
              <h2 className="text-3xl font-medium !text-paper sm:text-4xl">{t("dash.newCheck")}</h2>
              <p className="mt-2 max-w-md text-paper/75">{t("dash.newCheckBody")}</p>
              <span className="mt-6 inline-flex h-11 items-center gap-2 rounded-xl bg-ochre px-5 font-semibold text-ink transition-transform duration-300 group-hover:translate-x-1">
                {t("nav.diagnose")} <ArrowRight className="size-4" />
              </span>
            </div>
            <div className="relative hidden size-28 shrink-0 items-center justify-center rounded-3xl border border-paper/20 bg-paper/10 sm:flex">
              <ScanLine className="size-12 text-paper" strokeWidth={1.4} />
              <span className="absolute inset-x-4 top-4 h-0.5 animate-scan rounded-full bg-ochre shadow-[0_0_12px_var(--ochre)]" />
            </div>
          </div>
        </motion.div>
      </Link>

      {stats.isError ? (
        <ErrorState message={text((stats.error as Error).message)} onRetry={() => stats.refetch()} retryLabel={t("common.retry")} />
      ) : (
        <Stagger inView={false} className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StaggerItem><StatTile icon={ListChecks} label={t("dash.stat.total")} value={s?.total} tone="bg-paper-2 text-ink-2" /></StaggerItem>
          <StaggerItem><StatTile icon={CheckCircle2} label={t("dash.stat.healthy")} value={s?.healthy} tone="bg-leaf-50 text-leaf" /></StaggerItem>
          <StaggerItem><StatTile icon={TriangleAlert} label={t("dash.stat.attention")} value={s?.needs_attention} tone="bg-brick-50 text-brick" /></StaggerItem>
          <StaggerItem><StatTile icon={CloudOff} label={t("dash.stat.offline")} value={s?.offline} tone="bg-ochre-50 text-ochre-700" /></StaggerItem>
        </Stagger>
      )}

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <section>
          <h2 className="mb-4 text-2xl font-medium">{t("cal.title")}</h2>
          <FarmCalendar items={history.data ?? []} loading={history.isPending} />
        </section>
        <section className="flex flex-col">
          <h2 className="mb-4 text-2xl font-medium">{t("weather.heading")}</h2>
          <div className="flex-1"><WeatherCard /></div>
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <section>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-medium">{t("dash.recent")}</h2>
            <Link href="/history" className="group inline-flex items-center gap-1 text-sm font-bold text-leaf">
              {t("dash.viewAll")} <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
          {history.isPending ? (
            <div className="space-y-3">{[0, 1, 2].map((i) => <HistoryCardSkeleton key={i} />)}</div>
          ) : history.data?.length ? (
            <Stagger inView={false} className="space-y-3">
              {history.data.slice(0, 4).map((item) => (
                <StaggerItem key={item.id}><HistoryCard item={item} /></StaggerItem>
              ))}
            </Stagger>
          ) : (
            <EmptyState title={t("hist.empty")} body={t("hist.emptyBody")} action={<Button href="/diagnose">{t("dash.newCheck")}</Button>} />
          )}
        </section>

        <section>
          <h2 className="mb-4 text-2xl font-medium">{t("dash.split")}</h2>
          <Card className="p-6">
            <div className="flex items-center justify-between text-sm font-bold">
              <span className="flex items-center gap-2 text-leaf"><Sprout className="size-4" /> {t("common.crop")}</span>
              <span className="flex items-center gap-2 text-ochre-700">{t("common.livestock")} <Beef className="size-4" /></span>
            </div>
            <div className="mt-3 flex h-3 overflow-hidden rounded-full bg-paper-3">
              <motion.div className="h-full bg-leaf" initial={{ width: 0 }} animate={{ width: `${cropShare}%` }} transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1], delay: 0.3 }} />
              <motion.div className="h-full bg-ochre" initial={{ width: 0 }} animate={{ width: `${100 - cropShare}%` }} transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1], delay: 0.3 }} />
            </div>
            <div className="mt-3 flex justify-between font-display text-3xl font-semibold text-ink tabular-nums">
              <span>{s ? <CountUp key={lang} value={s.crop} format={n} /> : "–"}</span>
              <span>{s ? <CountUp key={lang} value={s.livestock} format={n} /> : "–"}</span>
            </div>
            {s && s.total > 0 && (
              <div className="mt-6 border-t border-line pt-5">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-semibold text-ink-2">{t("dash.stat.offline")}</span>
                  <span className="font-bold text-ink tabular-nums">{n(`${Math.round((s.offline / s.total) * 100)}%`)}</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-paper-3">
                  <motion.div className="h-full rounded-full bg-sage" initial={{ width: 0 }} animate={{ width: `${(s.offline / s.total) * 100}%` }} transition={{ duration: 1.1, delay: 0.5 }} />
                </div>
              </div>
            )}
          </Card>
        </section>
      </div>
    </div>
  );
}
