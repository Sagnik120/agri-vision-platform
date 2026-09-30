"use client";

import { ArrowLeft, ArrowRight, MessageSquareText, ShieldCheck, UserRound } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { StatusButton } from "@/components/jyotirmoydas/status-button";
import { Input, Label } from "@/components/ui/field";
import { OtpInput } from "@/components/ui/otp-input";
import { authApi } from "@/core/api/endpoints";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

import { DemoSms } from "./demo-sms";
import { PhoneField, isValidPhone } from "./phone-field";
import { useActionStatus } from "./use-action-state";

type Step = 1 | 2 | 3;
const RESEND_AFTER = 30;

const slide = {
  initial: (dir: number) => ({ opacity: 0, x: 40 * dir, filter: "blur(4px)" }),
  animate: { opacity: 1, x: 0, filter: "blur(0px)" },
  exit: (dir: number) => ({ opacity: 0, x: -40 * dir, filter: "blur(4px)" }),
};

export function SignupFlow({ onSwitchToLogin }: { onSwitchToLogin: () => void }) {
  const { t, text } = useI18n();
  const { signIn } = useSession();
  const router = useRouter();

  const [step, setStep] = useState<Step>(1);
  const [dir, setDir] = useState(1);
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [demoCode, setDemoCode] = useState<string | null>(null);
  const [verificationToken, setVerificationToken] = useState("");
  const [name, setName] = useState("");
  const [pin, setPin] = useState("");
  const [shake, setShake] = useState(0);
  const [cooldown, setCooldown] = useState(0);

  const sendAction = useActionStatus();
  const verifyAction = useActionStatus();
  const createAction = useActionStatus();

  useEffect(() => {
    if (cooldown <= 0) return;
    const id = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(id);
  }, [cooldown]);

  const go = (s: Step) => {
    setDir(s > step ? 1 : -1);
    setStep(s);
  };

  const sendOtp = async () => {
    try {
      const res = await sendAction.run(() => authApi.requestOtp(phone));
      if (!res) return;
      if (res.registered) {
        toast.info(t("auth.alreadyRegistered"));
        sendAction.reset();
        onSwitchToLogin();
        return;
      }
      setCode("");
      setCooldown(RESEND_AFTER);
      go(2);
      sendAction.reset();
      // Let the step transition land before the "SMS" arrives.
      setTimeout(() => setDemoCode(res.demo_otp), 700);
    } catch (e) {
      toast.error(text((e as Error).message));
    }
  };

  const verify = async (c = code) => {
    if (c.length !== 6) return;
    try {
      const res = await verifyAction.run(() => authApi.verifyOtp(phone, c));
      if (!res) return;
      setVerificationToken(res.verification_token);
      setDemoCode(null);
      setTimeout(() => {
        go(3);
        verifyAction.reset();
      }, 700);
    } catch (e) {
      setShake((n) => n + 1);
      toast.error(text((e as Error).message));
    }
  };

  const create = async () => {
    try {
      const session = await createAction.run(() => authApi.signup(verificationToken, name, pin));
      if (!session) return;
      signIn(session);
      setTimeout(() => router.replace("/dashboard"), 700);
    } catch (e) {
      toast.error(text((e as Error).message));
    }
  };

  return (
    <div>
      <DemoSms
        code={demoCode}
        onClose={() => setDemoCode(null)}
        onUse={(c) => {
          setCode(c);
          setDemoCode(null);
          verify(c);
        }}
      />

      {/* progress */}
      <div className="mb-7 flex items-center gap-3">
        {[1, 2, 3].map((n) => (
          <div key={n} className="h-1 flex-1 overflow-hidden rounded-full bg-paper-3">
            <motion.div
              className="h-full rounded-full bg-leaf"
              initial={false}
              animate={{ width: step >= n ? "100%" : "0%" }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            />
          </div>
        ))}
        <span className="text-xs font-semibold whitespace-nowrap text-ink-3 tabular-nums">{t("auth.step", { n: step })}</span>
      </div>

      <AnimatePresence mode="wait" custom={dir} initial={false}>
        <motion.div
          key={step}
          custom={dir}
          variants={slide}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        >
          {step === 1 && (
            <form
              className="space-y-6"
              onSubmit={(e) => {
                e.preventDefault();
                if (isValidPhone(phone)) sendOtp();
              }}
            >
              <PhoneField value={phone} onChange={setPhone} autoFocus />
              <StatusButton
                type="submit"
                variant={sendAction.variant}
                disabled={!isValidPhone(phone) || sendAction.state === "loading"}
                radius="lg"
                className="w-full"
                icon={<MessageSquareText className="size-5" />}
                text={{ loading: t("auth.sendingOtp"), success: t("auth.sendOtp"), error: t("auth.loginFail") }}
              >
                {t("auth.sendOtp")}
              </StatusButton>
            </form>
          )}

          {step === 2 && (
            <form
              className="space-y-6"
              onSubmit={(e) => {
                e.preventDefault();
                verify();
              }}
            >
              <div>
                <h3 className="flex items-center gap-2 font-sans text-lg font-bold">
                  <ShieldCheck className="size-5 text-leaf" /> {t("auth.otpTitle")}
                </h3>
                <p className="mt-1 text-sm text-ink-3">
                  {t("auth.otpSent", { phone: `${phone.slice(0, 5)} ${phone.slice(5)}` })} ·{" "}
                  <button type="button" onClick={() => go(1)} className="font-semibold text-leaf hover:underline">
                    {t("auth.changeNumber")}
                  </button>
                </p>
              </div>
              <OtpInput
                length={6}
                value={code}
                onChange={setCode}
                onComplete={verify}
                errorSignal={shake}
                success={verifyAction.state === "success"}
                autoFocus
                label={t("auth.otpTitle")}
              />
              <div className="flex items-center justify-between text-sm">
                <button
                  type="button"
                  disabled={cooldown > 0}
                  onClick={sendOtp}
                  className="font-semibold text-leaf disabled:cursor-default disabled:text-ink-3"
                >
                  {cooldown > 0 ? t("auth.resendIn", { s: cooldown }) : t("auth.resend")}
                </button>
              </div>
              <StatusButton
                type="submit"
                variant={verifyAction.variant}
                disabled={code.length !== 6 || verifyAction.state === "loading"}
                radius="lg"
                className="w-full"
                icon={<ShieldCheck className="size-5" />}
                text={{ loading: t("auth.verifying"), success: t("auth.verified"), error: t("auth.wrongCode") }}
              >
                {t("auth.verify")}
              </StatusButton>
            </form>
          )}

          {step === 3 && (
            <form
              className="space-y-6"
              onSubmit={(e) => {
                e.preventDefault();
                if (name.trim().length >= 2 && pin.length === 4) create();
              }}
            >
              <h3 className="flex items-center gap-2 font-sans text-lg font-bold">
                <UserRound className="size-5 text-leaf" /> {t("auth.profileTitle")}
              </h3>
              <div>
                <Label htmlFor="name">{t("auth.name")}</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder={t("auth.namePlaceholder")} autoFocus autoComplete="name" className="h-14 text-lg" />
              </div>
              <div>
                <Label>{t("auth.createPin")}</Label>
                <div className="max-w-[16rem]">
                  <OtpInput length={4} secret value={pin} onChange={setPin} success={createAction.state === "success"} label={t("auth.createPin")} />
                </div>
              </div>
              <div className="flex gap-3">
                <button type="button" onClick={() => go(2)} aria-label={t("common.back")} className="flex size-12 shrink-0 items-center justify-center rounded-xl border border-line-2 text-ink-2 transition-colors hover:bg-paper-2">
                  <ArrowLeft className="size-5" />
                </button>
                <StatusButton
                  type="submit"
                  variant={createAction.variant}
                  disabled={name.trim().length < 2 || pin.length !== 4 || createAction.state === "loading"}
                  radius="lg"
                  className="flex-1"
                  icon={<ArrowRight className="size-5" />}
                  text={{ loading: t("auth.creating"), success: t("auth.created"), error: t("auth.loginFail") }}
                >
                  {t("auth.create")}
                </StatusButton>
              </div>
            </form>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
