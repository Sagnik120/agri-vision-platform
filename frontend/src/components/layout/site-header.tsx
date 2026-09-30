"use client";

import { motion, useMotionValueEvent, useScroll } from "motion/react";
import Link from "next/link";
import { useState } from "react";

import { Logo } from "@/components/brand/logo";
import { ServerStatus } from "@/components/feedback/server-status";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

import { LanguageToggle } from "./language-toggle";

export function SiteHeader() {
  const { t } = useI18n();
  const { status } = useSession();
  const { scrollY } = useScroll();
  const [scrolled, setScrolled] = useState(false);
  useMotionValueEvent(scrollY, "change", (y) => setScrolled(y > 12));

  const links = [
    { href: "#why", label: t("nav.why") },
    { href: "#how", label: t("nav.how") },
    { href: "#zones", label: t("nav.zones") },
  ];

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="sticky top-0 z-50 px-4 pt-3 sm:px-6"
    >
      <div
        className={cn(
          "mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 rounded-2xl px-3 transition-all duration-500 sm:px-4",
          scrolled ? "border border-line bg-paper/80 shadow-[var(--shadow-soft)] backdrop-blur-xl" : "border border-transparent",
        )}
      >
        <Link href="/" aria-label="Agri-Vision home">
          <Logo />
        </Link>
        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="group relative rounded-lg px-3 py-2 text-sm font-semibold text-ink-2 transition-colors hover:text-ink">
              {l.label}
              <span className="absolute inset-x-3 bottom-1 h-px origin-left scale-x-0 bg-ochre transition-transform duration-300 group-hover:scale-x-100" />
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <ServerStatus className="hidden lg:inline-flex" />
          <LanguageToggle />
          {status === "authenticated" ? (
            <Button href="/dashboard" size="sm">{t("nav.openApp")}</Button>
          ) : (
            <>
              <Button href="/login" variant="ghost" size="sm" className="hidden sm:inline-flex">{t("nav.login")}</Button>
              <Button href="/login?mode=signup" size="sm">{t("nav.getStarted")}</Button>
            </>
          )}
        </div>
      </div>
    </motion.header>
  );
}
