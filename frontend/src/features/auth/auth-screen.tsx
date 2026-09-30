"use client";

import { ArrowLeft, CheckCircle2, ShieldCheck, Sprout } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { BlightLeaf } from "@/components/brand/illustrations";
import { Logo } from "@/components/brand/logo";
import { LanguageToggle } from "@/components/layout/language-toggle";
import { AdminLoginForm } from "@/features/admin/admin-login";
import { useAdminSession } from "@/features/admin/api";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

import { LoginForm } from "./login-form";
import { SignupFlow } from "./signup-flow";

export type Mode = "login" | "signup";
export type Role = "farmer" | "admin";

function SidePanel({ role }: { role: Role }) {
  const { t } = useI18n();
  const admin = role === "admin";
  const points = admin
    ? [t("admin.side.point1"), t("admin.side.point2"), t("admin.side.point3")]
    : [t("auth.side.point1"), t("auth.side.point2"), t("auth.side.point3")];
  return (
    <div
      className={cn(
        "relative hidden overflow-hidden p-10 text-paper transition-colors duration-700 lg:flex lg:flex-col lg:justify-between",
        admin ? "bg-ink" : "bg-leaf",
      )}
    >
      <div className="pointer-events-none absolute inset-0 opacity-[0.1] [background-image:radial-gradient(circle,#fff_1px,transparent_1px)] [background-size:22px_22px]" />
      <div className="pointer-events-none absolute -right-20 -bottom-20 size-[26rem] opacity-25">
        <BlightLeaf spots={false} className="rotate-[-18deg]" />
      </div>
      <div className="pointer-events-none absolute -top-32 -left-24 size-96 rounded-full bg-ochre/25 blur-3xl" />

      <Link href="/" className="relative inline-flex w-fit items-center gap-2 text-sm font-semibold text-paper/80 transition-colors hover:text-paper">
        <ArrowLeft className="size-4" /> {t("nav.home")}
      </Link>

      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={role}
          className="relative"
          initial={{ opacity: 0, y: 16, filter: "blur(6px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, y: -12, filter: "blur(6px)" }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
        >
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="max-w-md text-5xl leading-[1.08] font-medium !text-paper"
          >
            {admin ? t("admin.side.title") : t("auth.side.title")}
          </motion.h2>
          <p className="mt-5 max-w-sm text-lg text-paper/75">{admin ? t("admin.side.body") : t("auth.side.body")}</p>
          <ul className="mt-10 space-y-3">
            {points.map((p, i) => (
              <motion.li
                key={i}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + i * 0.12 }}
                className="flex items-center gap-3 font-semibold"
              >
                <CheckCircle2 className="size-5 text-ochre" /> {p}
              </motion.li>
            ))}
          </ul>
        </motion.div>
      </AnimatePresence>

      <p className="relative text-sm text-paper/55">{t("footer.note")}</p>
    </div>
  );
}

function RoleSwitch({ role, onChange }: { role: Role; onChange: (r: Role) => void }) {
  const { t } = useI18n();
  const options: { value: Role; label: string; icon: typeof Sprout }[] = [
    { value: "farmer", label: t("auth.role.farmer"), icon: Sprout },
    { value: "admin", label: t("auth.role.admin"), icon: ShieldCheck },
  ];
  return (
    <div role="radiogroup" aria-label={t("auth.role.label")} className="relative inline-flex h-10 rounded-full border border-line bg-surface p-1 shadow-[var(--shadow-soft)]">
      {options.map((o) => (
        <button
          key={o.value}
          role="radio"
          aria-checked={role === o.value}
          onClick={() => onChange(o.value)}
          className={cn(
            "relative z-10 inline-flex items-center gap-1.5 rounded-full px-4 text-sm font-bold transition-colors duration-300",
            role === o.value ? "text-paper" : "text-ink-3 hover:text-ink",
          )}
        >
          {role === o.value && (
            <motion.span
              layoutId="role-pill"
              className={cn("absolute inset-0 -z-10 rounded-full", o.value === "admin" ? "bg-ink" : "bg-leaf")}
              transition={{ type: "spring", stiffness: 420, damping: 32 }}
            />
          )}
          <o.icon className="size-4" />
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function AuthScreen({ initialMode, initialRole = "farmer" }: { initialMode: Mode; initialRole?: Role }) {
  const { t } = useI18n();
  const { status } = useSession();
  const admin = useAdminSession();
  const router = useRouter();
  const [mode, setMode] = useState<Mode>(initialMode);
  const [role, setRoleState] = useState<Role>(initialRole);

  // Keep the URL shareable (/login?role=admin) without a navigation.
  const setRole = (r: Role) => {
    setRoleState(r);
    window.history.replaceState(null, "", r === "admin" ? "/login?role=admin" : "/login");
  };

  useEffect(() => {
    if (role === "farmer" && status === "authenticated") router.replace("/dashboard");
    if (role === "admin" && admin.status === "authenticated") router.replace("/admin");
  }, [role, status, admin.status, router]);

  return (
    <div className="grid min-h-dvh lg:grid-cols-[1fr_1.1fr]">
      <SidePanel role={role} />
      <div className="relative flex flex-col px-5 py-6 sm:px-10">
        <div className="flex items-center justify-between">
          <Link href="/" className="lg:invisible">
            <Logo />
          </Link>
          <LanguageToggle />
        </div>

        <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center py-10">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-8">
            <RoleSwitch role={role} onChange={setRole} />
          </motion.div>

          <AnimatePresence mode="wait" initial={false}>
            {role === "admin" ? (
              <motion.div
                key="admin"
                initial={{ opacity: 0, x: 24, filter: "blur(6px)" }}
                animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                exit={{ opacity: 0, x: 24, filter: "blur(6px)" }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              >
                <h1 className="text-4xl font-medium sm:text-[2.6rem]">{t("admin.login.title")}</h1>
                <p className="mt-2 mb-8 text-ink-2">{t("admin.login.subtitle")}</p>
                <AdminLoginForm />
                <button onClick={() => setRole("farmer")} className="mt-6 text-sm font-bold text-leaf hover:underline">
                  {t("admin.login.farmer")}
                </button>
              </motion.div>
            ) : (
              <motion.div
                key="farmer"
                initial={{ opacity: 0, x: -24, filter: "blur(6px)" }}
                animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                exit={{ opacity: 0, x: -24, filter: "blur(6px)" }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              >
                <div>
                  <h1 className="text-4xl font-medium sm:text-[2.6rem]">{t("auth.welcome")}</h1>
                  <p className="mt-2 text-ink-2">{t("auth.subtitle")}</p>
                </div>

                <div role="tablist" className="relative mt-8 mb-8 grid grid-cols-2 rounded-xl bg-paper-2 p-1">
                  {(["login", "signup"] as Mode[]).map((m) => (
                    <button
                      key={m}
                      role="tab"
                      aria-selected={mode === m}
                      onClick={() => setMode(m)}
                      className={cn("relative z-10 h-10 rounded-lg text-sm font-bold transition-colors", mode === m ? "text-ink" : "text-ink-3 hover:text-ink-2")}
                    >
                      {mode === m && (
                        <motion.span layoutId="auth-tab" className="absolute inset-0 -z-10 rounded-lg bg-surface shadow-[var(--shadow-soft)]" transition={{ type: "spring", stiffness: 400, damping: 32 }} />
                      )}
                      {m === "login" ? t("auth.tab.login") : t("auth.tab.signup")}
                    </button>
                  ))}
                </div>

                <AnimatePresence mode="wait" initial={false}>
                  <motion.div
                    key={mode}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.25 }}
                  >
                    {mode === "login" ? <LoginForm /> : <SignupFlow onSwitchToLogin={() => setMode("login")} />}
                  </motion.div>
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
