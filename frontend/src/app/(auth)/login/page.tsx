import type { Metadata } from "next";

import { AuthScreen } from "@/features/auth/auth-screen";

export const metadata: Metadata = { title: "Log in" };

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const { mode, role } = await searchParams;
  return <AuthScreen initialMode={mode === "signup" ? "signup" : "login"} initialRole={role === "admin" ? "admin" : "farmer"} />;
}
