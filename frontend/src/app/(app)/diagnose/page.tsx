import type { Metadata } from "next";

import { DiagnoseView } from "@/features/diagnosis/diagnose-view";

export const metadata: Metadata = { title: "New check" };

export default function DiagnosePage() {
  return <DiagnoseView />;
}
