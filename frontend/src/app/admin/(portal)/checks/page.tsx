import type { Metadata } from "next";

import { ChecksView } from "@/features/admin/checks-view";

export const metadata: Metadata = { title: "All checks · Admin" };

export default function AdminChecksPage() {
  return <ChecksView />;
}
