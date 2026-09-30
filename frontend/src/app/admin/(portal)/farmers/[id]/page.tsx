import type { Metadata } from "next";

import { FarmerDetail } from "@/features/admin/farmers-view";

export const metadata: Metadata = { title: "Farmer · Admin" };

export default async function AdminFarmerPage({ params }: PageProps<"/admin/farmers/[id]">) {
  const { id } = await params;
  return <FarmerDetail id={decodeURIComponent(id)} />;
}
