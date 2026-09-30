"use client";

import { ArrowLeft, MapPin, UserRound } from "lucide-react";
import Link from "next/link";

import { ErrorState } from "@/components/feedback/empty-state";
import { Card } from "@/components/ui/card";
import { ResultView } from "@/features/diagnosis/result-view";
import { useI18n } from "@/providers/language-provider";

import { adminApi, useAdminCheck } from "./api";

export function CheckDetail({ id }: { id: number }) {
  const { t, n, region } = useI18n();
  const q = useAdminCheck(id);

  return (
    <div>
      <Link href="/admin/checks" className="group mb-6 inline-flex items-center gap-2 text-sm font-bold text-ink-2 transition-colors hover:text-leaf">
        <ArrowLeft className="size-4 transition-transform group-hover:-translate-x-1" /> {t("admin.backChecks")}
      </Link>
      {q.isPending ? (
        <div className="skeleton h-80 rounded-2xl" />
      ) : q.isError ? (
        <ErrorState message={(q.error as Error).message} onRetry={() => q.refetch()} retryLabel={t("common.retry")} />
      ) : (
        <div className="space-y-5">
          <Card className="flex flex-wrap items-center justify-between gap-4 p-5">
            <div className="flex items-center gap-3">
              <span className="flex size-11 items-center justify-center rounded-full bg-ochre-100 text-ochre-700"><UserRound className="size-5" /></span>
              <div>
                <p className="text-xs font-bold tracking-wide text-ink-3 uppercase">{t("admin.col.farmer")}</p>
                <p className="font-display text-xl font-semibold text-ink">{q.data.farmer_name}</p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="inline-flex h-9 items-center gap-2 rounded-full border border-line px-3.5 font-semibold text-ink-2">
                <MapPin className="size-4" /> {q.data.region ? region(q.data.region) : t("admin.unknownRegion")}
              </span>
              <span className="inline-flex h-9 items-center rounded-full border border-line px-3.5 font-semibold text-ink-2 tabular-nums">#{n(q.data.id)}</span>
              {q.data.vision_backend && (
                <span className="inline-flex h-9 items-center rounded-full border border-line px-3.5 font-mono text-xs text-ink-3">
                  {q.data.vision_backend}{q.data.advisory_backend ? ` · ${q.data.advisory_backend}` : ""}
                </span>
              )}
              <Link href={`/admin/farmers/${encodeURIComponent(q.data.farm_id)}`} className="inline-flex h-9 items-center rounded-full bg-leaf-50 px-3.5 font-bold text-leaf hover:bg-leaf-100">
                {t("admin.viewFarmer")}
              </Link>
            </div>
          </Card>
          <ResultView d={q.data} imageUrl={adminApi.imageUrl(q.data.id)} />
        </div>
      )}
    </div>
  );
}
