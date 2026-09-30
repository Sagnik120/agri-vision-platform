"use client";

import { ArrowDown, ArrowUp, Beef, ChevronRight, Cloud, Cpu, MessageSquareQuote, Sprout, Thermometer } from "lucide-react";
import { useRouter } from "next/navigation";

import { Badge } from "@/components/ui/card";
import { formatDate, parseDbDate } from "@/core/format";
import { Thumb } from "@/features/history/history-card";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import { type AdminCheck, adminApi } from "./api";

export type SortKey = "created_at" | "confidence" | "farmer_name" | "condition";

function Th({ label, k, sort, onSort, className }: { label: string; k?: SortKey; sort?: { key: SortKey; dir: 1 | -1 }; onSort?: (k: SortKey) => void; className?: string }) {
  const active = k && sort?.key === k;
  return (
    <th className={cn("px-3 pb-2.5 text-left text-xs font-bold whitespace-nowrap text-ink-3", className)}>
      {k && onSort ? (
        <button onClick={() => onSort(k)} className={cn("inline-flex items-center gap-1 hover:text-ink", active && "text-ink")}>
          {label}
          {active && (sort!.dir === 1 ? <ArrowUp className="size-3" /> : <ArrowDown className="size-3" />)}
        </button>
      ) : (
        label
      )}
    </th>
  );
}

export function ChecksTable({
  rows, compact, sort, onSort, hideFarmer,
}: {
  rows: AdminCheck[];
  compact?: boolean;
  sort?: { key: SortKey; dir: 1 | -1 };
  onSort?: (k: SortKey) => void;
  hideFarmer?: boolean;
}) {
  const { t, n, pct, lang, cond, region } = useI18n();
  const router = useRouter();

  if (!rows.length) return <p className="rounded-xl bg-paper-2 px-4 py-6 text-center text-sm text-ink-3">{t("admin.empty")}</p>;

  return (
    <div className="-mx-6 overflow-x-auto px-3">
      <table className="w-full min-w-[44rem] text-sm">
        <thead>
          <tr>
            <Th label={t("admin.col.when")} k="created_at" sort={sort} onSort={onSort} />
            {!hideFarmer && <Th label={t("admin.col.farmer")} k="farmer_name" sort={sort} onSort={onSort} />}
            <Th label={t("admin.col.condition")} k="condition" sort={sort} onSort={onSort} />
            <Th label={t("admin.col.confidence")} k="confidence" sort={sort} onSort={onSort} className="text-right" />
            <Th label={t("admin.col.route")} />
            {!compact && <Th label={t("admin.col.input")} />}
            <th className="w-6" />
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr
              key={r.id}
              onClick={() => router.push(`/admin/checks/${r.id}`)}
              className="group cursor-pointer border-t border-line transition-colors hover:bg-paper"
            >
              <td className="px-3 py-2.5 whitespace-nowrap">
                <p className="font-semibold text-ink tabular-nums">{n(formatDate(r.created_at, lang, { day: "numeric", month: "short" }))}</p>
                <p className="text-xs text-ink-3 tabular-nums">{n(parseDbDate(r.created_at).toLocaleTimeString(lang === "hi" ? "hi-IN" : "en-IN", { hour: "2-digit", minute: "2-digit", hour12: lang !== "hi" }))}</p>
              </td>
              {!hideFarmer && (
                <td className="px-3 py-2.5">
                  <p className="font-semibold text-ink">{r.farmer_name}</p>
                  <p className="text-xs text-ink-3">{r.region ? region(r.region) : t("admin.unknownRegion")}</p>
                </td>
              )}
              <td className="px-3 py-2.5">
                <div className="flex items-center gap-3">
                  <Thumb item={r} src={r.has_image ? adminApi.imageUrl(r.id) : undefined} className="size-10" />
                  <div className="min-w-0">
                    <p className="max-w-[16rem] truncate font-semibold text-ink first-letter:uppercase">{cond(r.condition)}</p>
                    <div className="mt-0.5 flex items-center gap-1.5">
                      <span className={cn("size-2 rounded-full", r.healthy ? "bg-sage" : r.confidence >= 0.75 ? "bg-brick" : "bg-amber")} />
                      <span className="flex items-center gap-1 text-xs text-ink-3">
                        {r.domain === "crop" ? <Sprout className="size-3" /> : <Beef className="size-3" />}
                        {r.domain === "crop" ? t("common.crop") : t("common.livestock")}
                      </span>
                    </div>
                  </div>
                </div>
              </td>
              <td className="px-3 py-2.5 text-right">
                <p className="font-display text-lg font-semibold text-ink tabular-nums">{pct(r.confidence)}</p>
              </td>
              <td className="px-3 py-2.5">
                <Badge tone={r.route === "cloud" ? "ochre" : "neutral"}>
                  {r.route === "cloud" ? <Cloud /> : <Cpu />}
                  {r.route === "cloud" ? t("res.cloud") : t("res.local")}
                </Badge>
              </td>
              {!compact && (
                <td className="max-w-[14rem] px-3 py-2.5">
                  <div className="flex items-center gap-1.5 text-xs text-ink-3">
                    {r.has_sensor && <Thermometer className="size-3.5 shrink-0 text-ochre-700" aria-label={t("admin.mix.sensor")} />}
                    {r.farmer_text ? (
                      <span className="flex min-w-0 items-center gap-1">
                        <MessageSquareQuote className="size-3.5 shrink-0" />
                        <span className="truncate italic">{r.farmer_text}</span>
                      </span>
                    ) : (
                      <span>{t("cal.photoOnly")}</span>
                    )}
                  </div>
                </td>
              )}
              <td className="pr-3">
                <ChevronRight className="size-4 text-ink-3 transition-transform group-hover:translate-x-0.5 group-hover:text-leaf" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
