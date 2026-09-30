"use client";

import {
  AlertTriangle, ArrowDownRight, ArrowUpRight, Beef, CloudCog, Download, Gauge, ListChecks, MapPinned, Minus, RefreshCw,
  Siren, Sprout, TriangleAlert, Users, WifiOff,
} from "lucide-react";
import { motion } from "motion/react";
import { useState } from "react";
import { toast } from "sonner";

import { ErrorState } from "@/components/feedback/empty-state";
import { Stagger, StaggerItem } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { timeAgo } from "@/core/format";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import { type PeriodSummary, adminApi, useOverview } from "./api";
import { BarList, CHART, ColumnChart, Sparkline } from "./charts";
import { ChecksTable } from "./checks-table";

const PERIODS = [7, 30, 90] as const;

function Delta({ now, prev, invert = false, asPoints = false }: { now: number; prev: number; invert?: boolean; asPoints?: boolean }) {
  const { n, t } = useI18n();
  if (!prev && !now) return <span className="text-xs text-ink-3">—</span>;
  const diff = asPoints ? (now - prev) * 100 : prev ? ((now - prev) / prev) * 100 : 100;
  const flat = Math.abs(diff) < 0.5;
  const good = invert ? diff < 0 : diff > 0;
  const Icon = flat ? Minus : diff > 0 ? ArrowUpRight : ArrowDownRight;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-0.5 rounded-full px-1.5 py-px text-[0.7rem] font-bold",
        flat ? "bg-paper-2 text-ink-3" : good ? "bg-leaf-50 text-leaf" : "bg-brick-50 text-brick",
      )}
      title={t("admin.vsPrev")}
    >
      <Icon className="size-3" />
      {n(`${Math.abs(Math.round(diff))}${asPoints ? "pt" : "%"}`)}
    </span>
  );
}

function Kpi({
  icon: Icon, label, value, sub, delta, spark, tone = "bg-paper-2 text-ink-2",
}: {
  icon: typeof ListChecks; label: string; value: string; sub?: string; delta?: React.ReactNode; spark?: number[]; tone?: string;
}) {
  return (
    <Card className="group relative flex h-full flex-col overflow-hidden p-5">
      <div className="flex items-center justify-between gap-2">
        <span className={cn("flex size-9 items-center justify-center rounded-xl transition-transform duration-500 group-hover:rotate-[-8deg]", tone)}>
          <Icon className="size-4.5" strokeWidth={1.8} />
        </span>
        {delta}
      </div>
      <p className="mt-4 font-display text-3xl font-semibold text-ink tabular-nums">{value}</p>
      <p className="mt-0.5 text-sm font-medium text-ink-3">{label}</p>
      {sub && <p className="mt-1 text-xs text-ink-3">{sub}</p>}
      {spark && <div className="mt-auto pt-3"><Sparkline values={spark} label={label} /></div>}
    </Card>
  );
}

function Section({ title, subtitle, action, children, className }: { title: string; subtitle?: string; action?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <Card className={cn("p-6", className)}>
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-sans text-lg font-bold">{title}</h2>
          {subtitle && <p className="mt-0.5 text-sm text-ink-3">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </Card>
  );
}

function SplitBar({ left, right, leftLabel, rightLabel, leftColor, rightColor }: { left: number; right: number; leftLabel: string; rightLabel: string; leftColor: string; rightColor: string }) {
  const { n, pct } = useI18n();
  const total = left + right;
  const share = total ? left / total : 0.5;
  return (
    <div>
      <div className="flex items-center justify-between text-sm font-semibold text-ink-2">
        <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-sm" style={{ background: leftColor }} />{leftLabel}</span>
        <span className="flex items-center gap-1.5">{rightLabel}<span className="size-2.5 rounded-sm" style={{ background: rightColor }} /></span>
      </div>
      <div className="mt-2 flex h-3 gap-[2px] overflow-hidden rounded-full bg-paper-3">
        <motion.div className="h-full" style={{ background: leftColor }} initial={{ width: 0 }} animate={{ width: `${share * 100}%` }} transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }} />
        <motion.div className="h-full flex-1" style={{ background: rightColor }} initial={{ opacity: 0 }} animate={{ opacity: total ? 1 : 0.3 }} />
      </div>
      <div className="mt-1.5 flex justify-between text-xs font-bold text-ink tabular-nums">
        <span>{n(left)} · {pct(share)}</span>
        <span>{n(right)} · {pct(total ? 1 - share : 0)}</span>
      </div>
    </div>
  );
}

const rate = (a: number, b: number) => (b ? a / b : 0);

export function OverviewView() {
  const { t, n, pct, lang, cond, region } = useI18n();
  const [days, setDays] = useState<(typeof PERIODS)[number]>(30);
  const q = useOverview(days);
  const [exporting, setExporting] = useState(false);
  const locale = lang === "hi" ? "hi-IN" : "en-IN";

  const exportCsv = async () => {
    setExporting(true);
    try {
      await adminApi.downloadCsv();
      toast.success(t("admin.exported"));
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setExporting(false);
    }
  };

  const header = (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p className="text-sm font-semibold text-ink-3">
          {q.data ? t("admin.updated", { t: timeAgo(q.data.generated_at, lang) }) : t("common.loading")}
        </p>
        <h1 className="mt-1 text-4xl font-medium sm:text-5xl">{t("admin.overview.title")}</h1>
        <p className="mt-2 text-ink-2">{t("admin.overview.subtitle")}</p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <div role="radiogroup" aria-label={t("admin.period")} className="relative flex h-9 rounded-full border border-line bg-surface p-0.5">
          {PERIODS.map((p) => (
            <button
              key={p}
              role="radio"
              aria-checked={days === p}
              onClick={() => setDays(p)}
              className={cn("relative z-10 rounded-full px-3.5 text-xs font-bold transition-colors", days === p ? "text-paper" : "text-ink-3 hover:text-ink")}
            >
              {days === p && <motion.span layoutId="period-pill" className="absolute inset-0 -z-10 rounded-full bg-ink" transition={{ type: "spring", stiffness: 420, damping: 32 }} />}
              {t("admin.days", { n: p })}
            </button>
          ))}
        </div>
        <Button variant="outline" size="sm" onClick={() => q.refetch()} aria-label={t("admin.refresh")}>
          <RefreshCw className={cn(q.isFetching && "animate-spin")} />
        </Button>
        <Button size="sm" onClick={exportCsv} loading={exporting}>
          {!exporting && <Download />} {t("admin.export")}
        </Button>
      </div>
    </div>
  );

  if (q.isError) return <div className="space-y-6">{header}<ErrorState message={(q.error as Error).message} onRetry={() => q.refetch()} retryLabel={t("common.retry")} /></div>;
  if (!q.data) {
    return (
      <div className="space-y-6">
        {header}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">{[0, 1, 2, 3].map((i) => <div key={i} className="skeleton h-40 rounded-2xl" />)}</div>
        <div className="skeleton h-80 rounded-2xl" />
      </div>
    );
  }

  const o = q.data;
  const c: PeriodSummary = o.current;
  const p: PeriodSummary = o.previous;
  const daily = o.daily.map((d) => d.crop + d.livestock);
  const dayLabel = (iso: string) => n(new Date(`${iso}T12:00:00`).toLocaleDateString(locale, { day: "numeric", month: "short" }));
  const hourLabel = (h: string) => n(`${h.padStart(2, "0")}:00`);
  const bucketLabel = (i: string) => n(`${Number(i) * 10}–${Number(i) * 10 + 10}%`);

  return (
    <div className="space-y-6">
      {header}

      {o.alerts.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} role="alert" className="rounded-2xl border border-[#eccabf] bg-brick-50 p-4 text-brick">
          <p className="flex items-center gap-2 text-sm font-bold"><Siren className="size-4" /> {t("admin.alerts.title")}</p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {o.alerts.map((a) => (
              <li key={`${a.condition}-${a.region}`} className="rounded-full border border-[#eccabf] bg-surface px-3 py-1 text-xs font-semibold">
                {cond(a.condition)} · {region(a.region)} · {t("admin.alerts.cases", { n: a.count })}
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      <Stagger inView={false} className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
        <StaggerItem>
          <Kpi icon={ListChecks} label={t("admin.kpi.checks")} value={n(c.checks)} delta={<Delta now={c.checks} prev={p.checks} />} spark={daily} sub={t("admin.kpi.allTime", { n: o.totals.all_time_checks })} />
        </StaggerItem>
        <StaggerItem>
          <Kpi icon={Users} label={t("admin.kpi.activeFarmers")} value={n(c.active_farmers)} tone="bg-leaf-50 text-leaf" delta={<Delta now={c.active_farmers} prev={p.active_farmers} />} sub={t("admin.kpi.registered", { n: o.totals.farmers, m: o.totals.new_farmers })} />
        </StaggerItem>
        <StaggerItem>
          <Kpi icon={TriangleAlert} label={t("admin.kpi.attention")} value={pct(rate(c.attention, c.checks))} tone="bg-brick-50 text-brick" delta={<Delta now={rate(c.attention, c.checks)} prev={rate(p.attention, p.checks)} invert asPoints />} sub={t("admin.kpi.cases", { n: c.attention })} />
        </StaggerItem>
        <StaggerItem>
          <Kpi icon={Gauge} label={t("admin.kpi.confidence")} value={pct(c.avg_confidence)} tone="bg-ochre-50 text-ochre-700" delta={<Delta now={c.avg_confidence} prev={p.avg_confidence} asPoints />} sub={t("admin.kpi.lowConf", { n: c.low_confidence })} />
        </StaggerItem>
        <StaggerItem>
          <Kpi icon={WifiOff} label={t("admin.kpi.offline")} value={pct(rate(c.local, c.checks))} tone="bg-leaf-50 text-leaf" delta={<Delta now={rate(c.local, c.checks)} prev={rate(p.local, p.checks)} asPoints />} sub={t("admin.kpi.local", { n: c.local })} />
        </StaggerItem>
        <StaggerItem>
          <Kpi icon={CloudCog} label={t("admin.kpi.cloud")} value={n(c.cloud)} tone="bg-ochre-50 text-ochre-700" delta={<Delta now={c.cloud} prev={p.cloud} invert />} sub={t("admin.kpi.cloudRate", { p: pct(rate(c.cloud, c.checks)) })} />
        </StaggerItem>
      </Stagger>

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <Section title={t("admin.chart.daily")} subtitle={t("admin.chart.dailySub", { n: days })}>
          <ColumnChart
            data={o.daily.map((d) => ({ label: d.date, values: { crop: d.crop, livestock: d.livestock } }))}
            series={[
              { key: "crop", name: t("common.crop"), color: CHART.crop },
              { key: "livestock", name: t("common.livestock"), color: CHART.livestock },
            ]}
            labelEvery={days <= 7 ? 1 : days <= 30 ? 5 : 15}
            formatLabel={dayLabel}
          />
        </Section>
        <Section title={t("admin.mix.title")} subtitle={t("admin.mix.sub")}>
          <div className="space-y-6">
            <SplitBar left={c.crop} right={c.livestock} leftLabel={t("common.crop")} rightLabel={t("common.livestock")} leftColor={CHART.crop} rightColor={CHART.livestock} />
            <SplitBar left={c.local} right={c.cloud} leftLabel={t("res.local")} rightLabel={t("res.cloud")} leftColor={CHART.crop} rightColor={CHART.livestock} />
            <SplitBar left={c.healthy} right={c.attention} leftLabel={t("hist.healthy")} rightLabel={t("hist.attention")} leftColor={CHART.crop} rightColor={CHART.livestock} />
            <div className="grid grid-cols-2 gap-3 border-t border-line pt-5">
              <div className="rounded-xl bg-paper-2 p-3">
                <p className="font-display text-2xl font-semibold text-ink">{pct(rate(c.with_notes, c.checks))}</p>
                <p className="text-xs font-medium text-ink-3">{t("admin.mix.notes")}</p>
              </div>
              <div className="rounded-xl bg-paper-2 p-3">
                <p className="font-display text-2xl font-semibold text-ink">{n(c.with_sensor)}</p>
                <p className="text-xs font-medium text-ink-3">{t("admin.mix.sensor")}</p>
              </div>
            </div>
          </div>
        </Section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Section title={t("admin.top.title")} subtitle={t("admin.top.sub")}>
          <BarList
            emptyLabel={t("admin.empty")}
            rows={o.top_conditions.map((x) => ({
              key: x.condition,
              label: (
                <span className="flex items-center gap-2">
                  {x.domain === "crop" ? <Sprout className="size-4 shrink-0 text-ink-3" /> : <Beef className="size-4 shrink-0 text-ink-3" />}
                  <span className="truncate first-letter:uppercase">{cond(x.condition)}</span>
                </span>
              ),
              value: x.count,
              color: x.domain === "crop" ? CHART.crop : CHART.livestock,
              meta: t("admin.top.meta", { c: pct(x.avg_confidence), k: x.cloud }),
            }))}
          />
        </Section>
        <Section title={t("admin.regions.title")} subtitle={t("admin.regions.sub")} action={<MapPinned className="size-5 text-ink-3" />}>
          {o.regions.length === 0 ? (
            <p className="rounded-xl bg-paper-2 px-4 py-3 text-sm text-ink-3">{t("admin.empty")}</p>
          ) : (
            <div className="max-h-80 overflow-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-surface text-left text-xs text-ink-3">
                  <tr>
                    <th className="pb-2 font-bold">{t("admin.col.region")}</th>
                    <th className="pb-2 text-right font-bold">{t("admin.col.farmers")}</th>
                    <th className="pb-2 text-right font-bold">{t("admin.col.checks")}</th>
                    <th className="w-28 pb-2 pl-4 font-bold">{t("admin.col.attention")}</th>
                  </tr>
                </thead>
                <tbody>
                  {o.regions.map((r) => {
                    const share = rate(r.attention, r.checks);
                    return (
                      <tr key={r.region} className="border-t border-line">
                        <td className="py-2.5 font-semibold text-ink-2">{r.region === "Unknown" ? t("admin.unknownRegion") : region(r.region)}</td>
                        <td className="py-2.5 text-right text-ink tabular-nums">{n(r.farmers)}</td>
                        <td className="py-2.5 text-right font-bold text-ink tabular-nums">{n(r.checks)}</td>
                        <td className="py-2.5 pl-4">
                          <div className="flex items-center gap-2">
                            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-paper-2">
                              <div className="h-full rounded-full bg-brick" style={{ width: `${share * 100}%` }} />
                            </div>
                            <span className="w-9 text-right text-xs font-bold text-ink-2 tabular-nums">{pct(share)}</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Section title={t("admin.conf.title")} subtitle={t("admin.conf.sub")} action={<AlertTriangle className="size-5 text-ink-3" />}>
          <ColumnChart
            height={160}
            data={o.confidence_buckets.map((v, i) => ({ label: String(i), values: { checks: v } }))}
            series={[{ key: "checks", name: t("admin.col.checks"), color: CHART.crop }]}
            labelEvery={2}
            formatLabel={(l) => n(`${Number(l) * 10}%`)}
            formatTip={bucketLabel}
          />
        </Section>
        <Section title={t("admin.hours.title")} subtitle={t("admin.hours.sub")}>
          <ColumnChart
            height={160}
            data={o.hours_ist.map((v, i) => ({ label: String(i), values: { checks: v } }))}
            series={[{ key: "checks", name: t("admin.col.checks"), color: CHART.crop }]}
            labelEvery={6}
            formatLabel={hourLabel}
          />
        </Section>
      </div>

      <Section title={t("admin.recent")} action={<Button href="/admin/checks" variant="ghost" size="sm">{t("dash.viewAll")}</Button>}>
        <ChecksTable rows={o.recent} compact />
      </Section>
    </div>
  );
}
