import type { Metadata } from "next";

import { SystemView } from "@/features/admin/system-view";

export const metadata: Metadata = { title: "System · Admin" };

export default function AdminSystemPage() {
  return <SystemView />;
}
