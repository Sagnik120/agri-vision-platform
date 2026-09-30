import type { Metadata } from "next";

import { AdminLogin } from "@/features/admin/admin-login";

export const metadata: Metadata = { title: "Admin login" };

export default function AdminLoginPage() {
  return <AdminLogin />;
}
