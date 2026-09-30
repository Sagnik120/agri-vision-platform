import type { Metadata } from "next";

import { HistoryDetail } from "@/features/history/history-detail";

export const metadata: Metadata = { title: "Diagnosis" };

export default async function HistoryDetailPage({ params }: PageProps<"/history/[id]">) {
  const { id } = await params;
  return <HistoryDetail id={Number(id)} />;
}
