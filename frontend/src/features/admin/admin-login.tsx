"use client";

import { ArrowRight, Eye, EyeOff, KeyRound, UserRound } from "lucide-react";
import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/field";
import { useI18n } from "@/providers/language-provider";

import { adminApi, useAdminSession } from "./api";

/** Username + password form for the admin portal; used on /login (Admin tab) and /admin/login. */
export function AdminLoginForm() {
  const { t, text } = useI18n();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [shake, setShake] = useState(0);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;
    setBusy(true);
    try {
      await adminApi.login(username, password);
      toast.success(t("admin.login.ok"));
      router.replace("/admin");
    } catch (err) {
      setShake((s) => s + 1);
      setPassword("");
      toast.error(text((err as Error).message));
    } finally {
      setBusy(false);
    }
  };

  return (
    <motion.form
      key={shake}
      animate={shake ? { x: [0, -10, 10, -6, 6, 0] } : {}}
      transition={{ duration: 0.4 }}
      onSubmit={submit}
      className="space-y-6"
    >
      <div>
        <Label htmlFor="admin-user" className="flex items-center gap-2"><UserRound className="size-4 text-ink-3" /> {t("admin.login.username")}</Label>
        <Input id="admin-user" autoComplete="username" autoFocus value={username} onChange={(e) => setUsername(e.target.value)} />
      </div>
      <div>
        <Label htmlFor="admin-pass" className="flex items-center gap-2"><KeyRound className="size-4 text-ink-3" /> {t("admin.login.password")}</Label>
        <div className="relative">
          <Input
            id="admin-pass"
            type={show ? "text" : "password"}
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pr-12"
          />
          <button
            type="button"
            onClick={() => setShow((s) => !s)}
            aria-label={show ? t("admin.login.hide") : t("admin.login.show")}
            className="absolute top-1/2 right-2 flex size-9 -translate-y-1/2 items-center justify-center rounded-lg text-ink-3 transition-colors hover:bg-paper-2 hover:text-ink"
          >
            {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        </div>
      </div>
      <Button type="submit" size="lg" variant="primary" className="w-full !bg-ink hover:!bg-ink-2" loading={busy} disabled={!username || !password}>
        {t("admin.login.submit")} {!busy && <ArrowRight />}
      </Button>
    </motion.form>
  );
}

/** /admin/login keeps working (bookmarks, admin shell redirects) by opening the Admin tab of the main login. */
export function AdminLogin() {
  const router = useRouter();
  const { status } = useAdminSession();
  useEffect(() => {
    if (status === "loading") return;
    router.replace(status === "authenticated" ? "/admin" : "/login?role=admin");
  }, [status, router]);
  return null;
}
