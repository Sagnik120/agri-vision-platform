"use client";

import { Activity, ClipboardList, LayoutDashboard, LogOut, ShieldCheck, Smartphone, Users, type LucideIcon } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { Logo, LogoMark } from "@/components/brand/logo";
import { ServerStatus } from "@/components/feedback/server-status";
import { LanguageToggle } from "@/components/layout/language-toggle";
import type { MessageKey } from "@/core/i18n";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import { adminSignOut, useAdminSession } from "./api";

const ADMIN_NAV: { href: string; label: MessageKey; icon: LucideIcon; exact?: boolean }[] = [
  { href: "/admin", label: "admin.nav.overview", icon: LayoutDashboard, exact: true },
  { href: "/admin/checks", label: "admin.nav.checks", icon: ClipboardList },
  { href: "/admin/farmers", label: "admin.nav.farmers", icon: Users },
  { href: "/admin/system", label: "admin.nav.system", icon: Activity },
];

const isActive = (pathname: string, href: string, exact?: boolean) =>
  exact ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);

export function AdminShell({ children }: { children: React.ReactNode }) {
  const { t } = useI18n();
  const pathname = usePathname();
  const router = useRouter();
  const { status, user } = useAdminSession();

  useEffect(() => {
    if (status === "anonymous") router.replace("/login?role=admin");
  }, [status, router]);

  if (status !== "authenticated") {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <motion.div animate={{ scale: [1, 1.08, 1] }} transition={{ repeat: Infinity, duration: 1.4 }}>
          <LogoMark className="size-12" />
        </motion.div>
      </div>
    );
  }

  const signOut = () => {
    adminSignOut();
    router.replace("/login?role=admin");
  };

  return (
    <div className="flex min-h-dvh">
      <aside className="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col border-r border-line bg-surface/70 px-4 py-6 backdrop-blur lg:flex">
        <Link href="/admin" className="px-2">
          <Logo />
        </Link>
        <span className="mt-3 ml-2 inline-flex w-fit items-center gap-1.5 rounded-full bg-ink px-2.5 py-0.5 text-[0.7rem] font-bold text-paper">
          <ShieldCheck className="size-3.5" /> {t("admin.badge")}
        </span>
        <nav className="mt-8 flex flex-col gap-1">
          {ADMIN_NAV.map((item) => {
            const active = isActive(pathname, item.href, item.exact);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group relative flex h-11 items-center gap-3 rounded-xl px-3 text-[0.95rem] font-semibold transition-colors",
                  active ? "text-leaf" : "text-ink-2 hover:bg-paper-2 hover:text-ink",
                )}
              >
                {active && (
                  <motion.span layoutId="admin-active" className="absolute inset-0 -z-10 rounded-xl bg-leaf-50" transition={{ type: "spring", stiffness: 380, damping: 32 }} />
                )}
                {active && <motion.span layoutId="admin-bar" className="absolute top-2.5 bottom-2.5 -left-4 w-1 rounded-r-full bg-leaf" />}
                <item.icon className="size-5 transition-transform duration-300 group-hover:scale-110" strokeWidth={1.8} />
                {t(item.label)}
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto rounded-2xl border border-line bg-paper p-3">
          <div className="flex items-center gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-ink font-display text-sm font-semibold text-paper">
              <ShieldCheck className="size-4.5" />
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-bold text-ink">{user}</p>
              <p className="truncate text-xs text-ink-3">{t("admin.role")}</p>
            </div>
          </div>
          <button
            onClick={signOut}
            className="mt-3 flex h-9 w-full items-center justify-center gap-2 rounded-lg text-sm font-semibold text-ink-3 transition-colors hover:bg-brick-50 hover:text-brick"
          >
            <LogOut className="size-4" /> {t("nav.logout")}
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-3 border-b border-line/70 bg-paper/75 px-4 backdrop-blur-xl sm:px-8">
          <Link href="/admin" className="flex items-center gap-2 lg:hidden">
            <Logo compact />
            <span className="rounded-full bg-ink px-2 py-0.5 text-[0.65rem] font-bold text-paper">{t("admin.badge")}</span>
          </Link>
          <ServerStatus className="hidden sm:inline-flex" />
          <div className="ml-auto flex items-center gap-2">
            <Link
              href="/dashboard"
              className="hidden h-8 items-center gap-1.5 rounded-full border border-line bg-surface/80 px-3 text-xs font-semibold text-ink-2 transition-colors hover:border-leaf/40 hover:text-leaf md:inline-flex"
            >
              <Smartphone className="size-3.5" /> {t("admin.farmerApp")}
            </Link>
            <LanguageToggle />
            <button onClick={signOut} aria-label={t("nav.logout")} className="flex size-8 items-center justify-center rounded-full text-ink-3 transition-colors hover:bg-brick-50 hover:text-brick lg:hidden">
              <LogOut className="size-4" />
            </button>
          </div>
        </header>
        <main id="main" className="flex-1 px-4 pt-6 pb-28 sm:px-8 lg:pb-12">{children}</main>
      </div>

      <nav className="fixed inset-x-3 bottom-3 z-40 flex h-16 items-center justify-around rounded-2xl border border-line bg-surface/90 px-2 shadow-[var(--shadow-lift)] backdrop-blur-xl lg:hidden">
        {ADMIN_NAV.map((item) => {
          const active = isActive(pathname, item.href, item.exact);
          return (
            <Link key={item.href} href={item.href} className="relative flex w-16 flex-col items-center gap-1 py-1">
              <item.icon className={cn("size-5 transition-colors", active ? "text-leaf" : "text-ink-3")} strokeWidth={1.8} />
              <span className={cn("text-[0.65rem] font-bold", active ? "text-leaf" : "text-ink-3")}>{t(item.label)}</span>
              {active && <motion.span layoutId="admin-tab-dot" className="absolute -bottom-1 size-1 rounded-full bg-leaf" />}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
