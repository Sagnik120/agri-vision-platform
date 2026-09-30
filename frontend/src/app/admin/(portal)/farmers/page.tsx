import type { Metadata } from "next";

import { FarmersView } from "@/features/admin/farmers-view";

export const metadata: Metadata = { title: "Farmers · Admin" };

export default function AdminFarmersPage() {
  return <FarmersView />;
}
