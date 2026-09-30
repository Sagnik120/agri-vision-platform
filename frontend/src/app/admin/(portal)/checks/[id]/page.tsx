import type { Metadata } from "next";

import { CheckDetail } from "@/features/admin/check-detail";

export const metadata: Metadata = { title: "Check · Admin" };

export default async function AdminCheckPage({ params }: PageProps<"/admin/checks/[id]">) {
  const { id } = await params;
  return <CheckDetail id={Number(id)} />;
}
