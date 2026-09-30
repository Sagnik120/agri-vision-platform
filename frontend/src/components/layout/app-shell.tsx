"use client";

import { LogOut } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { Logo, LogoMark } from "@/components/brand/logo";
import { ServerStatus } from "@/components/feedback/server-status";
import { APP_NAV } from "@/config/nav";
import { useMe } from "@/features/farm/queries";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

import { LanguageToggle } from "./language-toggle";

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

function Initials({ name }: { name?: string }) {
  const init = (name ?? "?").split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
  return (
    <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-ochre-100 font-display text-sm font-semibold text-ochre-700">
      {init}
    </span>
  );
}

function Sidebar() {
  const { t, region } = useI18n();
  const pathname = usePathname();
  const { farmer, signOut } = useSession();

  return (
    <aside className="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col border-r border-line bg-surface/70 px-4 py-6 backdrop-blur lg:flex">
      <Link href="/" className="px-2">
        <Logo />
      </Link>
      <nav className="mt-10 flex flex-col gap-1">
        {APP_NAV.map((item) => {
          const active = isActive(pathname, item.href);
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
                <motion.span
                  layoutId="sidebar-active"
                  className="absolute inset-0 -z-10 rounded-xl bg-leaf-50"
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                />
              )}
              {active && <motion.span layoutId="sidebar-bar" className="absolute top-2.5 bottom-2.5 -left-4 w-1 rounded-r-full bg-leaf" />}
              <item.icon className="size-5 transition-transform duration-300 group-hover:scale-110" strokeWidth={1.8} />
              {t(item.label)}
              {item.primary && !active && <span className="ml-auto size-1.5 rounded-full bg-ochre" />}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-2xl border border-line bg-paper p-3">
        <div className="flex items-center gap-3">
          <Initials name={farmer?.name} />
          <div className="min-w-0">
            <p className="truncate text-sm font-bold text-ink">{farmer?.name ?? "…"}</p>
            <p className="truncate text-xs text-ink-3">{farmer?.region ? region(farmer.region) : `+91 ${farmer?.phone ?? ""}`}</p>
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
  );
}

function MobileTabBar() {
  const { t } = useI18n();
  const pathname = usePathname();
  return (
    <nav className="fixed inset-x-3 bottom-3 z-40 flex h-16 items-center justify-around rounded-2xl border border-line bg-surface/90 px-2 shadow-[var(--shadow-lift)] backdrop-blur-xl lg:hidden">
      {APP_NAV.map((item) => {
        const active = isActive(pathname, item.href);
        if (item.primary) {
          return (
            <Link key={item.href} href={item.href} aria-label={t(item.label)} className="-mt-8">
              <motion.span
                whileTap={{ scale: 0.9 }}
                className={cn(
                  "flex size-14 items-center justify-center rounded-2xl text-paper shadow-[0_10px_24px_-8px_var(--leaf)] ring-4 ring-paper",
                  active ? "bg-leaf-700" : "bg-leaf",
                )}
              >
                <item.icon className="size-6" />
              </motion.span>
            </Link>
          );
        }
        return (
          <Link key={item.href} href={item.href} className="relative flex w-16 flex-col items-center gap-1 py-1">
            <item.icon className={cn("size-5 transition-colors", active ? "text-leaf" : "text-ink-3")} strokeWidth={1.8} />
            <span className={cn("text-[0.65rem] font-bold", active ? "text-leaf" : "text-ink-3")}>{t(item.label)}</span>
            {active && <motion.span layoutId="tab-dot" className="absolute -bottom-1 size-1 rounded-full bg-leaf" />}
          </Link>
        );
      })}
    </nav>
  );
}

function AppLoading() {
  return (
    <div className="flex min-h-dvh items-center justify-center">
      <motion.div animate={{ scale: [1, 1.08, 1] }} transition={{ repeat: Infinity, duration: 1.4 }}>
        <LogoMark className="size-12" />
      </motion.div>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { status, setFarmer } = useSession();
  const router = useRouter();
  const me = useMe(status === "authenticated");

  useEffect(() => {
    if (status === "anonymous") router.replace("/login");
  }, [status, router]);

  useEffect(() => {
    if (me.data) setFarmer(me.data);
  }, [me.data, setFarmer]);

  if (status !== "authenticated") return <AppLoading />;

  return (
    <div className="flex min-h-dvh">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-3 border-b border-line/70 bg-paper/75 px-4 backdrop-blur-xl sm:px-8">
          <Link href="/dashboard" className="lg:hidden">
            <Logo compact />
          </Link>
          <ServerStatus />
          <LanguageToggle className="ml-auto" />
        </header>
        <main id="main" className="flex-1 px-4 pt-6 pb-28 sm:px-8 lg:pb-12">{children}</main>
      </div>
      <MobileTabBar />
    </div>
  );
}
