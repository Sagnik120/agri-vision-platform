"use client";

import {
  AlertOctagon, BookMarked, CalendarRange, CloudSun, Cpu, Cloud, FlaskConical, Info, Lightbulb, MessageSquareQuote,
  Printer, ShieldAlert, ShieldCheck, Square, TriangleAlert, Volume2,
} from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";

import CoolCheckbox from "@/components/daddy/cool-checkbox";
import { ConfidenceRing } from "@/components/feedback/confidence-ring";
import { Stagger, StaggerItem } from "@/components/motion/reveal";
import { Badge, Card } from "@/components/ui/card";
import { diagnosisApi } from "@/core/api/endpoints";
import { formatDate, healthOf } from "@/core/format";
import type { MessageKey } from "@/core/i18n";
import type { Diagnosis } from "@/core/types";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import { Brackets } from "./photo-dropzone";

const HEALTH_TONE = { healthy: "leaf", watch: "amber", disease: "brick" } as const;

function Panel({ icon: Icon, title, children, className }: { icon: typeof Info; title: string; children: React.ReactNode; className?: string }) {
  return (
    <Card className={cn("p-6", className)}>
      <h3 className="flex items-center gap-2 font-sans text-sm font-bold tracking-wide text-ink-2 uppercase">
        <Icon className="size-4 text-leaf" /> {title}
      </h3>
      <div className="mt-4">{children}</div>
    </Card>
  );
}

function Callout({ tone, icon: Icon, children }: { tone: "amber" | "brick" | "ochre" | "leaf"; icon: typeof Info; children: React.ReactNode }) {
  const tones = {
    amber: "border-[#f1dfb4] bg-amber-50 text-[#7a5a14]",
    brick: "border-[#eccabf] bg-brick-50 text-brick",
    ochre: "border-ochre-100 bg-ochre-50 text-ochre-700",
    leaf: "border-leaf-100 bg-leaf-50 text-leaf",
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      role={tone === "brick" ? "alert" : undefined}
      className={cn("flex gap-3 rounded-2xl border px-4 py-3.5 text-sm font-medium", tones[tone])}
    >
      <Icon className="mt-0.5 size-4 shrink-0" />
      <div>{children}</div>
    </motion.div>
  );
}

/** Reads the advice aloud with the browser's speech engine (works offline on most phones). */
function useSpeak(text: string) {
  const [speaking, setSpeaking] = useState(false);
  const supported = typeof window !== "undefined" && "speechSynthesis" in window;
  useEffect(() => () => void (supported && window.speechSynthesis.cancel()), [supported]);
  const toggle = () => {
    if (!supported) return;
    if (speaking) {
      window.speechSynthesis.cancel();
      return setSpeaking(false);
    }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = /[ऀ-ॿ]/.test(text) ? "hi-IN" : "en-IN";
    u.rate = 0.95;
    u.onend = u.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(u);
    setSpeaking(true);
  };
  return { supported, speaking, toggle };
}

export function ResultView({ d, footer, imageUrl }: { d: Diagnosis; footer?: React.ReactNode; imageUrl?: string }) {
  const { t, lang, n, pct, cond, text } = useI18n();
  const health = healthOf(d.condition, d.confidence);
  const actions = d.actions.map(text);
  const [done, setDone] = useState<number[]>([]);
  const isMock = (d.vision_backend ?? "").startsWith("mock");
  const speech = useSpeak([cond(d.condition), text(d.summary), ...actions].filter(Boolean).join(". "));
  const certaintyKey = `res.certainty.${d.certainty ?? "possible"}` as MessageKey;

  return (
    <div className="space-y-5">
      {/* Headline */}
      <Card className="overflow-hidden">
        <div className="grid md:grid-cols-[minmax(0,19rem)_1fr]">
          <div className="relative aspect-[4/3] bg-paper-2 md:aspect-auto md:min-h-72">
            {d.has_image ? (
              <motion.img
                initial={{ scale: 1.08, filter: "blur(8px)" }}
                animate={{ scale: 1, filter: "blur(0px)" }}
                transition={{ duration: 0.8 }}
                src={imageUrl ?? diagnosisApi.imageUrl(d.id)}
                alt=""
                className="absolute inset-0 h-full w-full object-cover"
              />
            ) : (
              <div className="dotted-bg absolute inset-0" />
            )}
            <Brackets className="border-paper/80" />
          </div>
          <div className="flex flex-col gap-5 p-6 sm:p-8">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={d.route === "cloud" ? "ochre" : "leaf"}>
                {d.route === "cloud" ? <Cloud /> : <Cpu />}
                {d.route === "cloud" ? t("res.cloud") : t("res.local")}
              </Badge>
              <Badge>{d.domain === "crop" ? t("common.crop") : t("common.livestock")}</Badge>
              <Badge tone={HEALTH_TONE[health]}>{t(certaintyKey)}</Badge>
              {d.created_at && <span className="text-xs font-medium text-ink-3">{n(formatDate(d.created_at, lang, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }))}</span>}
            </div>
            <div className="flex items-start justify-between gap-6">
              <div className="min-w-0">
                <motion.h2
                  initial={{ opacity: 0, y: 10, filter: "blur(6px)" }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  transition={{ duration: 0.6 }}
                  className="text-3xl leading-tight font-medium first-letter:uppercase sm:text-4xl"
                >
                  {cond(d.condition)}
                </motion.h2>
                {d.summary && <p className="mt-3 leading-relaxed text-ink-2">{text(d.summary)}</p>}
              </div>
              <ConfidenceRing value={d.confidence} label={t("res.confidence")} className="shrink-0" />
            </div>
            <div className="no-print mt-auto flex flex-wrap gap-2">
              {speech.supported && (
                <button onClick={speech.toggle} className="inline-flex h-9 items-center gap-2 rounded-lg border border-line-2 bg-surface px-3 text-sm font-semibold text-ink-2 transition-colors hover:bg-paper-2">
                  {speech.speaking ? <Square className="size-3.5 fill-current" /> : <Volume2 className="size-4" />}
                  {t("res.listen")}
                </button>
              )}
              <button onClick={() => window.print()} className="inline-flex h-9 items-center gap-2 rounded-lg border border-line-2 bg-surface px-3 text-sm font-semibold text-ink-2 transition-colors hover:bg-paper-2">
                <Printer className="size-4" /> {t("res.print")}
              </button>
            </div>
          </div>
        </div>
      </Card>

      {/* Alerts */}
      {d.expert_consultation_recommended && <Callout tone="brick" icon={AlertOctagon}>{t("res.expert")}</Callout>}
      {isMock && <Callout tone="ochre" icon={FlaskConical}>{t("res.mock")}</Callout>}
      {d.quality_flag === "warn" && <Callout tone="amber" icon={TriangleAlert}>{t("res.lowQuality")}</Callout>}

      <div className="grid gap-5 lg:grid-cols-[1.35fr_1fr]">
        <div className="space-y-5">
          {actions.length > 0 && (
            <Panel icon={Lightbulb} title={t("res.whatToDo")}>
              <CoolCheckbox
                className="-mx-2.5"
                todos={actions.map((a, i) => ({ id: i, title: a, checked: done.includes(i) }))}
                onToggle={(id) => setDone((xs) => (xs.includes(id) ? xs.filter((x) => x !== id) : [...xs, id]))}
              />
            </Panel>
          )}
          {d.warning && !/^none\b/i.test(d.warning) && (
            <Callout tone="amber" icon={ShieldAlert}>
              <span className="font-bold">{t("res.warning")}: </span>
              {text(d.warning)}
            </Callout>
          )}
          {d.safety_note && <Callout tone="leaf" icon={Info}>{text(d.safety_note)}</Callout>}
          {d.context?.note && (
            <Panel icon={CalendarRange} title={t("res.context")}>
              <p className="leading-relaxed text-ink-2">{text(d.context.note)}</p>
            </Panel>
          )}
          {d.farmer_text && (
            <Panel icon={MessageSquareQuote} title={t("res.yourNotes")}>
              <p className="font-display text-lg leading-relaxed text-ink-2 italic">“{d.farmer_text}”</p>
            </Panel>
          )}
        </div>

        <div className="space-y-5">
          {(d.top_predictions.length > 0 || d.reason) && (
            <Panel icon={Cpu} title={t("res.why")}>
              {d.top_predictions.length > 0 && (
                <>
                  <p className="mb-3 text-xs font-bold text-ink-3 uppercase">{t("res.alternatives")}</p>
                  <Stagger inView={false} className="space-y-3">
                    {d.top_predictions.map((p, i) => (
                      <StaggerItem key={i}>
                        <div className="flex items-center justify-between text-sm">
                          <span className={cn("font-semibold first-letter:uppercase", i === 0 ? "text-ink" : "text-ink-2")}>{cond(p.label)}</span>
                          <span className="font-bold text-ink tabular-nums">{pct(p.confidence)}</span>
                        </div>
                        <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-paper-3">
                          <motion.div
                            className={cn("h-full rounded-full", i === 0 ? "bg-leaf" : "bg-line-2")}
                            initial={{ width: 0 }}
                            animate={{ width: `${Math.max(2, p.confidence * 100)}%` }}
                            transition={{ duration: 0.9, delay: 0.3 + i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                          />
                        </div>
                      </StaggerItem>
                    ))}
                  </Stagger>
                </>
              )}
              {d.evidence_agreement && (
                <div className="mt-5 flex items-center justify-between border-t border-line pt-4 text-sm">
                  <span className="font-semibold text-ink-2">{t("res.evidence")}</span>
                  <Badge tone={d.evidence_agreement === "high" ? "leaf" : d.evidence_agreement === "medium" ? "amber" : "brick"} className="capitalize">
                    {t(`res.evidence.${d.evidence_agreement}` as MessageKey)}
                  </Badge>
                </div>
              )}
              {d.reason && <p className="mt-4 rounded-xl bg-paper-2 p-3 text-sm leading-relaxed text-ink-2">{text(d.reason)}</p>}
            </Panel>
          )}

          {d.citations.length > 0 && (
            <Panel icon={BookMarked} title={t("res.sources")}>
              <ul className="space-y-2.5">
                {d.citations.map((c, i) => (
                  <li key={i} className="flex gap-2.5 text-sm leading-relaxed text-ink-2">
                    <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-md bg-ochre-50 text-[0.65rem] font-bold text-ochre-700">{n(i + 1)}</span>
                    {c}
                  </li>
                ))}
              </ul>
              {d.citation_check?.citations_valid !== undefined && (
                <p className={cn("mt-4 flex items-center gap-1.5 text-xs font-bold", d.citation_check.citations_valid ? "text-leaf" : "text-amber")}>
                  {d.citation_check.citations_valid ? <ShieldCheck className="size-4" /> : <ShieldAlert className="size-4" />}
                  {d.citation_check.citations_valid ? t("res.verified") : t("res.unverified")}
                </p>
              )}
            </Panel>
          )}

          {d.weather && d.weather.temperature_c !== undefined && (
            <Panel icon={CloudSun} title={t("res.weather")}>
              <div className="grid grid-cols-3 gap-3 text-center">
                {[
                  [n(`${d.weather.temperature_c}°C`), t("res.temp")],
                  [n(`${d.weather.relative_humidity_pct}%`), t("res.humidity")],
                  [n(`${d.weather.precipitation_last_7d_mm} mm`), t("res.rain7d")],
                ].map(([v, l]) => (
                  <div key={l} className="rounded-xl bg-paper-2 py-3">
                    <p className="font-display text-lg font-semibold text-ink">{v}</p>
                    <p className="text-xs text-ink-3">{l}</p>
                  </div>
                ))}
              </div>
            </Panel>
          )}
        </div>
      </div>

      {footer}
    </div>
  );
}
