"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";

import { ErrorState } from "@/components/feedback/empty-state";
import { Card } from "@/components/ui/card";
import { ResultView } from "@/features/diagnosis/result-view";
import { useDiagnosis } from "@/features/farm/queries";
import { useI18n } from "@/providers/language-provider";

function DetailSkeleton() {
  return (
    <Card className="grid overflow-hidden md:grid-cols-[19rem_1fr]">
      <div className="skeleton aspect-[4/3] rounded-none md:aspect-auto md:min-h-72" />
      <div className="space-y-4 p-8">
        <div className="skeleton h-5 w-40" />
        <div className="skeleton h-10 w-2/3" />
        <div className="skeleton h-4 w-full" />
        <div className="skeleton h-4 w-4/5" />
      </div>
    </Card>
  );
}

export function HistoryDetail({ id }: { id: number }) {
  const { t, text } = useI18n();
  const q = useDiagnosis(id);

  return (
    <div>
      <Link href="/history" className="group mb-6 inline-flex items-center gap-2 text-sm font-bold text-ink-2 transition-colors hover:text-leaf">
        <ArrowLeft className="size-4 transition-transform group-hover:-translate-x-1" /> {t("res.backHistory")}
      </Link>
      {q.isPending ? (
        <DetailSkeleton />
      ) : q.isError ? (
        <ErrorState message={text((q.error as Error).message)} onRetry={() => q.refetch()} retryLabel={t("common.retry")} />
      ) : (
        <ResultView d={q.data} />
      )}
    </div>
  );
}
