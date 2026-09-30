"use client";

import { ArrowRight, KeyRound } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { StatusButton } from "@/components/jyotirmoydas/status-button";
import { Label } from "@/components/ui/field";
import { OtpInput } from "@/components/ui/otp-input";
import { authApi } from "@/core/api/endpoints";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

import { PhoneField, isValidPhone } from "./phone-field";
import { useActionStatus } from "./use-action-state";

export function LoginForm() {
  const { t, text } = useI18n();
  const { signIn } = useSession();
  const router = useRouter();
  const [phone, setPhone] = useState("");
  const [pin, setPin] = useState("");
  const [shake, setShake] = useState(0);
  const action = useActionStatus();

  const canSubmit = isValidPhone(phone) && pin.length === 4 && action.state !== "loading" && action.state !== "success";

  const submit = async (p = pin) => {
    if (!isValidPhone(phone) || p.length !== 4) return;
    try {
      const session = await action.run(() => authApi.login(phone, p));
      if (!session) return;
      signIn(session);
      toast.success(`${t("auth.loginOk")}, ${session.farmer.name.split(" ")[0]}`);
      setTimeout(() => router.replace("/dashboard"), 650);
    } catch (e) {
      setShake((n) => n + 1);
      setPin("");
      toast.error(text((e as Error).message));
    }
  };

  return (
    <form
      className="space-y-6"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <PhoneField value={phone} onChange={setPhone} autoFocus />
      <div>
        <Label className="flex items-center gap-2">
          <KeyRound className="size-4 text-ink-3" /> {t("auth.pin")}
        </Label>
        <div className="max-w-[16rem]">
          <OtpInput
            length={4}
            secret
            value={pin}
            onChange={setPin}
            onComplete={(v) => isValidPhone(phone) && submit(v)}
            errorSignal={shake}
            success={action.state === "success"}
            label={t("auth.pin")}
          />
        </div>
      </div>
      <StatusButton
        type="submit"
        variant={action.variant}
        disabled={!canSubmit}
        radius="lg"
        className="w-full"
        icon={<ArrowRight className="size-5" />}
        text={{ loading: t("auth.loggingIn"), success: t("auth.loginOk"), error: t("auth.loginFail") }}
      >
        {t("auth.login")}
      </StatusButton>
    </form>
  );
}
