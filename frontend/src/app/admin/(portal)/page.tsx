import type { Metadata } from "next";

import { OverviewView } from "@/features/admin/overview-view";

export const metadata: Metadata = { title: "Admin" };

export default function AdminOverviewPage() {
  return <OverviewView />;
}
