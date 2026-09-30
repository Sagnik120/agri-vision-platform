"use client";

import { ChevronLeft, ChevronRight, Download, Search, SlidersHorizontal, X } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { ErrorState } from "@/components/feedback/empty-state";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { parseDbDate } from "@/core/format";
import type { MessageKey } from "@/core/i18n";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import { type AdminCheck, adminApi, useAdminChecks } from "./api";
import { ChecksTable, type SortKey } from "./checks-table";

const PAGE = 20;

type Filters = { domain: string; route: string; health: string; region: string; from: string; to: string };
const EMPTY: Filters = { domain: "", route: "", health: "", region: "", from: "", to: "" };

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "h-8 rounded-full border px-3 text-xs font-bold transition-colors",
        active ? "border-ink bg-ink text-paper" : "border-line bg-surface text-ink-2 hover:border-line-2",
      )}
    >
      {children}
    </button>
  );
}

const matches = (r: AdminCheck, f: Filters) => {
  if (f.domain && r.domain !== f.domain) return false;
  if (f.route && r.route !== f.route) return false;
  if (f.health === "healthy" && !r.healthy) return false;
  if (f.health === "attention" && r.healthy) return false;
  if (f.health === "low" && r.confidence >= 0.5) return false;
  if (f.region && (r.region ?? "") !== f.region) return false;
  const d = parseDbDate(r.created_at);
  if (f.from && d < new Date(`${f.from}T00:00:00`)) return false;
  if (f.to && d > new Date(`${f.to}T23:59:59`)) return false;
  return true;
};

export function ChecksView() {
  const { t, n, cond, region: regionName } = useI18n();
  const q = useAdminChecks();
  const [query, setQuery] = useState("");
  const [f, setF] = useState<Filters>(EMPTY);
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: "created_at", dir: -1 });
  const [page, setPage] = useState(0);
  const [exporting, setExporting] = useState(false);

  const set = (patch: Partial<Filters>) => {
    setF((x) => ({ ...x, ...patch }));
    setPage(0);
  };
  const toggle = (k: keyof Filters, v: string) => set({ [k]: f[k] === v ? "" : v });

  const regions = useMemo(() => [...new Set((q.data ?? []).map((r) => r.region).filter(Boolean) as string[])].sort(), [q.data]);

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const out = (q.data ?? []).filter(
      (r) =>
        matches(r, f) &&
        (!needle ||
          [r.condition, cond(r.condition), r.farmer_name, r.farmer_text, r.region ?? "", String(r.id)].some((x) => x.toLowerCase().includes(needle))),
    );
    return out.sort((a, b) => {
      const av = a[sort.key];
      const bv = b[sort.key];
      const cmp = typeof av === "number" && typeof bv === "number" ? av - bv : String(av).localeCompare(String(bv));
      return cmp * sort.dir;
    });
  }, [q.data, f, query, sort, cond]);

  const pages = Math.max(1, Math.ceil(rows.length / PAGE));
  const current = rows.slice(page * PAGE, page * PAGE + PAGE);
  const active = Object.values(f).some(Boolean) || !!query;

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

  const dim = (k: MessageKey) => <span className="mr-1 text-[0.7rem] font-bold tracking-wide text-ink-3 uppercase">{t(k)}</span>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-medium sm:text-5xl">{t("admin.checks.title")}</h1>
          <p className="mt-2 text-ink-2">{t("admin.checks.subtitle")}</p>
        </div>
        <Button size="sm" onClick={exportCsv} loading={exporting}>
          {!exporting && <Download />} {t("admin.export")}
        </Button>
      </div>

      <Card className="space-y-4 p-5">
        <div className="flex flex-wrap items-center gap-3">
          <label className="relative min-w-60 flex-1">
            <Search className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-ink-3" />
            <input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(0);
              }}
              placeholder={t("admin.checks.search")}
              className="h-10 w-full rounded-full border border-line bg-surface pr-4 pl-10 text-sm text-ink outline-none transition-[border-color,box-shadow] placeholder:text-ink-3 focus:border-leaf focus:shadow-[0_0_0_4px_var(--leaf-50)]"
            />
          </label>
          <div className="flex items-center gap-2 text-xs">
            <input type="date" value={f.from} max={f.to || undefined} onChange={(e) => set({ from: e.target.value })} aria-label={t("admin.from")} className="h-10 rounded-full border border-line bg-surface px-3 text-ink-2 outline-none focus:border-leaf" />
            <span className="text-ink-3">–</span>
            <input type="date" value={f.to} min={f.from || undefined} onChange={(e) => set({ to: e.target.value })} aria-label={t("admin.to")} className="h-10 rounded-full border border-line bg-surface px-3 text-ink-2 outline-none focus:border-leaf" />
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
          <SlidersHorizontal className="size-4 text-ink-3" />
          <div className="flex flex-wrap items-center gap-1.5">
            {dim("admin.f.domain")}
            <Chip active={f.domain === "crop"} onClick={() => toggle("domain", "crop")}>{t("common.crop")}</Chip>
            <Chip active={f.domain === "livestock"} onClick={() => toggle("domain", "livestock")}>{t("common.livestock")}</Chip>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {dim("admin.f.route")}
            <Chip active={f.route === "local"} onClick={() => toggle("route", "local")}>{t("res.local")}</Chip>
            <Chip active={f.route === "cloud"} onClick={() => toggle("route", "cloud")}>{t("res.cloud")}</Chip>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {dim("admin.f.health")}
            <Chip active={f.health === "healthy"} onClick={() => toggle("health", "healthy")}>{t("hist.healthy")}</Chip>
            <Chip active={f.health === "attention"} onClick={() => toggle("health", "attention")}>{t("hist.attention")}</Chip>
            <Chip active={f.health === "low"} onClick={() => toggle("health", "low")}>{t("admin.f.lowConf")}</Chip>
          </div>
          {regions.length > 0 && (
            <select
              value={f.region}
              onChange={(e) => set({ region: e.target.value })}
              aria-label={t("admin.col.region")}
              className="h-8 rounded-full border border-line bg-surface px-3 text-xs font-bold text-ink-2 outline-none focus:border-leaf"
            >
              <option value="">{t("admin.f.allRegions")}</option>
              {regions.map((r) => <option key={r} value={r}>{regionName(r)}</option>)}
            </select>
          )}
          {active && (
            <button
              onClick={() => {
                setF(EMPTY);
                setQuery("");
                setPage(0);
              }}
              className="ml-auto inline-flex items-center gap-1 text-xs font-bold text-brick hover:underline"
            >
              <X className="size-3.5" /> {t("admin.clear")}
            </button>
          )}
        </div>
      </Card>

      <Card className="p-6">
        {q.isError ? (
          <ErrorState message={(q.error as Error).message} onRetry={() => q.refetch()} retryLabel={t("common.retry")} />
        ) : q.isPending ? (
          <div className="space-y-3">{[0, 1, 2, 3, 4].map((i) => <div key={i} className="skeleton h-14 rounded-xl" />)}</div>
        ) : (
          <>
            <p className="mb-4 text-sm font-semibold text-ink-3">
              {t("admin.showing", { a: rows.length ? page * PAGE + 1 : 0, b: Math.min(rows.length, (page + 1) * PAGE), n: rows.length })}
            </p>
            <ChecksTable
              rows={current}
              sort={sort}
              onSort={(key) => setSort((s) => ({ key, dir: s.key === key ? ((-s.dir) as 1 | -1) : -1 }))}
            />
            {pages > 1 && (
              <div className="mt-5 flex items-center justify-end gap-2">
                <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage((p) => p - 1)} aria-label={t("cal.prev")}><ChevronLeft /></Button>
                <span className="text-sm font-bold text-ink-2 tabular-nums">{n(`${page + 1} / ${pages}`)}</span>
                <Button variant="outline" size="sm" disabled={page >= pages - 1} onClick={() => setPage((p) => p + 1)} aria-label={t("cal.next")}><ChevronRight /></Button>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
}
