"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Globe2, LogOut, MapPin, Server, UserRound } from "lucide-react";
import { motion } from "motion/react";
import { toast } from "sonner";

import { useHealth } from "@/components/feedback/server-status";
import { Stagger, StaggerItem } from "@/components/motion/reveal";
import { Badge, Card } from "@/components/ui/card";
import { Hint, Label, Select } from "@/components/ui/field";
import { farmApi } from "@/core/api/endpoints";
import { formatDate } from "@/core/format";
import { LANGS, type Lang, type MessageKey, dictionaries } from "@/core/i18n";
import { queryKeys, useMeta } from "@/features/farm/queries";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";
import { useSession } from "@/providers/session-provider";

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-line py-3.5 last:border-0">
      <span className="text-sm font-semibold text-ink-3">{label}</span>
      <span className="text-right text-sm font-bold text-ink">{children}</span>
    </div>
  );
}

function SectionCard({ icon: Icon, title, children }: { icon: typeof UserRound; title: string; children: React.ReactNode }) {
  return (
    <Card className="p-6">
      <h2 className="flex items-center gap-2.5 font-sans text-lg font-bold">
        <span className="flex size-9 items-center justify-center rounded-xl bg-leaf-50 text-leaf"><Icon className="size-4.5" /></span>
        {title}
      </h2>
      <div className="mt-4">{children}</div>
    </Card>
  );
}

const LANG_NAMES: Record<Lang, { native: string; en: string }> = {
  en: { native: "English", en: "English" },
  hi: { native: "हिन्दी", en: "Hindi" },
};

export function SettingsView() {
  const { t, lang, setLang, n, region: regionName, text } = useI18n();
  const { farmer, setFarmer, signOut } = useSession();
  const meta = useMeta();
  const health = useHealth();
  const qc = useQueryClient();
  // Known backend values get a friendly, translated name; anything new is shown as sent.
  const label = (prefix: "set.mode" | "set.adv", v: string) => {
    const key = `${prefix}.${v}` as MessageKey;
    return key in dictionaries.en ? t(key) : v;
  };

  const region = useMutation({
    mutationFn: (r: string) => farmApi.update({ region: r }),
    onSuccess: (f) => {
      setFarmer(f);
      qc.setQueryData(queryKeys.me, f);
      toast.success(t("set.regionSaved"), { description: f.region ? regionName(f.region) : undefined });
    },
    onError: (e) => toast.error(text((e as Error).message)),
  });

  return (
    <div>
      <h1 className="text-4xl font-medium sm:text-5xl">{t("set.title")}</h1>
      <Stagger inView={false} className="mt-8 grid gap-5 lg:grid-cols-2">
        <StaggerItem>
          <SectionCard icon={UserRound} title={t("set.profile")}>
            <Row label={t("set.name")}>{farmer?.name}</Row>
            <Row label={t("set.phone")}>+91 {farmer?.phone}</Row>
            {farmer?.created_at && <Row label={t("set.memberSince")}>{n(formatDate(farmer.created_at, lang))}</Row>}
            <button onClick={signOut} className="mt-4 inline-flex h-10 items-center gap-2 rounded-xl px-3 text-sm font-bold text-brick transition-colors hover:bg-brick-50">
              <LogOut className="size-4" /> {t("nav.logout")}
            </button>
          </SectionCard>
        </StaggerItem>

        <StaggerItem>
          <SectionCard icon={MapPin} title={t("set.farm")}>
            <Label htmlFor="region">{t("set.region")}</Label>
            <Select
              id="region"
              value={farmer?.region ?? ""}
              disabled={region.isPending || !meta.data}
              onChange={(e) => e.target.value && region.mutate(e.target.value)}
            >
              <option value="" disabled>{t("set.choose")}</option>
              {meta.data?.regions.map((r) => <option key={r} value={r}>{regionName(r)}</option>)}
            </Select>
            <Hint>{t("set.regionHint")}</Hint>
          </SectionCard>
        </StaggerItem>

        <StaggerItem>
          <SectionCard icon={Globe2} title={t("set.language")}>
            <div className="grid grid-cols-2 gap-3">
              {LANGS.map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={cn(
                    "relative rounded-2xl border-[1.5px] p-4 text-left transition-colors",
                    lang === l ? "border-leaf bg-leaf-50" : "border-line hover:border-line-2 hover:bg-paper-2",
                  )}
                >
                  <span className="block font-display text-2xl font-semibold text-ink">{LANG_NAMES[l].native}</span>
                  <span className="text-xs font-semibold text-ink-3">{LANG_NAMES[l].en}</span>
                  {lang === l && (
                    <motion.span layoutId="lang-check" className="absolute top-3 right-3 flex size-6 items-center justify-center rounded-full bg-leaf text-paper">
                      <Check className="size-3.5" strokeWidth={3} />
                    </motion.span>
                  )}
                </button>
              ))}
            </div>
          </SectionCard>
        </StaggerItem>

        <StaggerItem>
          <SectionCard icon={Server} title={t("set.system")}>
            <Row label={t("set.server")}>
              {health.isPending ? <span className="skeleton inline-block h-4 w-16" /> : health.isError ? <Badge tone="brick">{t("status.offline")}</Badge> : <Badge tone="leaf">{t("set.ready")}</Badge>}
            </Row>
            <Row label={t("set.mode")}>{health.data ? label("set.mode", health.data.expert_mode) : "—"}</Row>
            <Row label={t("set.advisory")}>{health.data ? label("set.adv", health.data.advisory_backend) : "—"}</Row>
            <Row label={t("set.cloud")}>
              {health.data ? <Badge tone={health.data.cloud_ready ? "leaf" : "ochre"}>{health.data.cloud_ready ? t("set.ready") : t("set.notConfigured")}</Badge> : "—"}
            </Row>
          </SectionCard>
        </StaggerItem>
      </Stagger>
    </div>
  );
}
