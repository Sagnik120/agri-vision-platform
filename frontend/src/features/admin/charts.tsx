"use client";

import { Table2 } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

/**
 * Chart hues, validated for colour-blind separation against the white surface.
 * #3a8048 is the brand leaf nudged up in chroma so it doesn't read grey as a mark;
 * the ochre is below 3:1 contrast, so every chart carries a legend/labels + table view.
 */
export const CHART = { crop: "#3a8048", livestock: "#c8963e" } as const;

export interface Series { key: string; name: string; color: string }

function niceMax(v: number) {
  if (v <= 4) return 4;
  const p = 10 ** Math.floor(Math.log10(v));
  return ([1, 2, 4, 6, 8, 10].map((m) => m * p).find((c) => c >= v) ?? 10 * p);
}

function Legend({ series }: { series: Series[] }) {
  return (
    <div className="flex flex-wrap gap-3 text-xs font-semibold text-ink-2">
      {series.map((s) => (
        <span key={s.key} className="flex items-center gap-1.5">
          <span className="size-2.5 rounded-sm" style={{ background: s.color }} />
          {s.name}
        </span>
      ))}
    </div>
  );
}

function TableToggle({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  const { t } = useI18n();
  return (
    <button
      onClick={onToggle}
      aria-pressed={open}
      className={cn(
        "inline-flex h-7 items-center gap-1.5 rounded-full border px-2.5 text-[0.7rem] font-bold transition-colors",
        open ? "border-leaf bg-leaf-50 text-leaf" : "border-line text-ink-3 hover:text-ink-2",
      )}
    >
      <Table2 className="size-3.5" /> {t("admin.table")}
    </button>
  );
}

/** Stacked (or single-series) columns with a per-column hover tooltip and a table view. */
export function ColumnChart({
  data, series, labelEvery = 1, height = 200, formatLabel, formatTip,
}: {
  data: { label: string; values: Record<string, number> }[];
  series: Series[];
  labelEvery?: number;
  height?: number;
  formatLabel?: (label: string) => string;
  formatTip?: (label: string) => string;
}) {
  const { n } = useI18n();
  const [hover, setHover] = useState<number | null>(null);
  const [table, setTable] = useState(false);
  const totals = data.map((d) => series.reduce((a, s) => a + (d.values[s.key] ?? 0), 0));
  const max = niceMax(Math.max(1, ...totals));
  const ticks = [0, max / 2, max];
  const fl = formatLabel ?? ((l: string) => l);

  return (
    <div>
      <div className="mb-3 flex items-center justify-between gap-3">
        {series.length > 1 ? <Legend series={series} /> : <span />}
        <TableToggle open={table} onToggle={() => setTable((v) => !v)} />
      </div>
      {table ? (
        <div className="max-h-64 overflow-auto rounded-xl border border-line">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-paper-2 text-left text-xs text-ink-3">
              <tr>
                <th className="px-3 py-2 font-bold" />
                {series.map((s) => <th key={s.key} className="px-3 py-2 text-right font-bold">{s.name}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <tr key={d.label} className="border-t border-line">
                  <td className="px-3 py-1.5 font-medium text-ink-2">{(formatTip ?? fl)(d.label)}</td>
                  {series.map((s) => <td key={s.key} className="px-3 py-1.5 text-right font-semibold text-ink tabular-nums">{n(d.values[s.key] ?? 0)}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="relative pl-8">
          <div className="relative" style={{ height }}>
            {ticks.map((tk) => (
              <div key={tk} className="absolute inset-x-0 border-t border-line" style={{ bottom: `${(tk / max) * 100}%` }}>
                <span className="absolute -top-2 -left-8 w-6 text-right text-[0.65rem] font-medium text-ink-3 tabular-nums">{n(Math.round(tk))}</span>
              </div>
            ))}
            <div className="absolute inset-0 flex items-end gap-[2px]">
              {data.map((d, i) => (
                <div
                  key={d.label}
                  className="relative flex h-full flex-1 cursor-default items-end justify-center"
                  onPointerEnter={() => setHover(i)}
                  onPointerLeave={() => setHover((h) => (h === i ? null : h))}
                >
                  {hover === i && <div className="absolute inset-0 rounded-md bg-paper-2" />}
                  <motion.div
                    className="relative flex w-full max-w-6 flex-col-reverse gap-[2px]"
                    initial={{ height: 0 }}
                    animate={{ height: `${(totals[i] / max) * 100}%` }}
                    transition={{ duration: 0.7, delay: Math.min(i, 30) * 0.012, ease: [0.22, 1, 0.36, 1] }}
                  >
                    {series.map((s, si) => {
                      const v = d.values[s.key] ?? 0;
                      if (!v) return null;
                      const isTop = series.slice(si + 1).every((x) => !(d.values[x.key] ?? 0));
                      return (
                        <div
                          key={s.key}
                          className={cn("w-full", isTop && "rounded-t")}
                          style={{ flexGrow: v, flexBasis: 0, background: s.color, minHeight: 2 }}
                        />
                      );
                    })}
                  </motion.div>
                  <AnimatePresence>
                    {hover === i && (
                      <motion.div
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className={cn(
                          "pointer-events-none absolute bottom-full z-20 mb-2 min-w-32 rounded-xl border border-line bg-surface px-3 py-2 text-xs shadow-[var(--shadow-lift)]",
                          i > data.length * 0.7 ? "right-0" : i < data.length * 0.3 ? "left-0" : "left-1/2 -translate-x-1/2",
                        )}
                      >
                        <p className="font-bold text-ink">{(formatTip ?? fl)(d.label)}</p>
                        {series.map((s) => (
                          <p key={s.key} className="mt-1 flex items-center justify-between gap-4 text-ink-2">
                            <span className="flex items-center gap-1.5">
                              <span className="size-2 rounded-sm" style={{ background: s.color }} />
                              {s.name}
                            </span>
                            <span className="font-bold text-ink tabular-nums">{n(d.values[s.key] ?? 0)}</span>
                          </p>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-2 flex gap-[2px]">
            {data.map((d, i) => (
              <span key={d.label} className="relative h-4 flex-1">
                {i % labelEvery === 0 && (
                  <span className="absolute left-1/2 -translate-x-1/2 text-[0.65rem] font-medium whitespace-nowrap text-ink-3">{fl(d.label)}</span>
                )}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/** Ranked horizontal bars, value at the tip; single hue unless a row overrides it. */
export function BarList({
  rows, color = CHART.crop, emptyLabel,
}: {
  rows: { key: string; label: React.ReactNode; value: number; display?: string; color?: string; meta?: React.ReactNode }[];
  color?: string;
  emptyLabel?: string;
}) {
  const { n } = useI18n();
  const max = Math.max(1, ...rows.map((r) => r.value));
  if (!rows.length) return <p className="rounded-xl bg-paper-2 px-4 py-3 text-sm text-ink-3">{emptyLabel}</p>;
  return (
    <ul className="space-y-3">
      {rows.map((r, i) => (
        <li key={r.key} className="group">
          <div className="flex items-baseline justify-between gap-3 text-sm">
            <span className="min-w-0 truncate font-semibold text-ink-2 group-hover:text-ink">{r.label}</span>
            <span className="shrink-0 text-xs text-ink-3">{r.meta}</span>
          </div>
          <div className="mt-1.5 flex items-center gap-2">
            <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-paper-2">
              <motion.div
                className="h-full rounded-full"
                style={{ background: r.color ?? color }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.max(2, (r.value / max) * 100)}%` }}
                transition={{ duration: 0.8, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] }}
              />
            </div>
            <span className="w-12 text-right text-sm font-bold text-ink tabular-nums">{r.display ?? n(r.value)}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}

/** Tiny inline trend for KPI tiles (no axes, decorative + aria summary). */
export function Sparkline({ values, color = CHART.crop, label }: { values: number[]; color?: string; label: string }) {
  const max = Math.max(1, ...values);
  const w = 100;
  const h = 28;
  const pts = values.map((v, i) => [(i / Math.max(1, values.length - 1)) * w, h - (v / max) * (h - 4) - 2]);
  const d = pts.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" className="h-7 w-full" role="img" aria-label={label}>
      <path d={`${d} L${w},${h} L0,${h} Z`} fill={color} opacity={0.1} />
      <path d={d} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}
