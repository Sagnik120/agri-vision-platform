"use client";

import { ChevronDown, HeartPulse, NotebookPen, Stethoscope, Thermometer } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

import CoolCheckbox from "@/components/daddy/cool-checkbox";
import SubSelectToggle, { type MenuItem } from "@/components/daddy/sub-select-toggle";
import { Hint, Label, Select, Textarea } from "@/components/ui/field";
import type { MessageKey } from "@/core/i18n";
import type { DomainChoice, SensorLevel, SensorReading } from "@/core/types";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

export const CROP_SYMPTOMS: MessageKey[] = ["sym.spots", "sym.yellow", "sym.wilting", "sym.holes"];
export const LIVESTOCK_SYMPTOMS: MessageKey[] = ["sym.fever", "sym.appetite", "sym.limping", "sym.blisters"];

export interface DetailsValue {
  domain: DomainChoice;
  symptoms: MessageKey[];
  notes: string;
  sensorOn: boolean;
  sensor: SensorReading;
  season: string;
}

export const DEFAULT_DETAILS: DetailsValue = {
  domain: "auto",
  symptoms: [],
  notes: "",
  sensorOn: false,
  sensor: { temperature: 38.5, activity: "normal", feed_intake: "normal" },
  season: "",
};

function Section({ icon: Icon, title, hint, children }: { icon: typeof Stethoscope; title: string; hint?: string; children: React.ReactNode }) {
  return (
    <section className="border-t border-line pt-5 first:border-0 first:pt-0">
      <h3 className="flex items-center gap-2 font-sans text-[0.95rem] font-bold text-ink">
        <Icon className="size-4 text-leaf" /> {title}
      </h3>
      {hint && <p className="mt-0.5 text-xs text-ink-3">{hint}</p>}
      <div className="mt-3">{children}</div>
    </section>
  );
}

function LevelPicker({ value, onChange, label }: { value: SensorLevel; onChange: (v: SensorLevel) => void; label: string }) {
  const { t } = useI18n();
  const levels: SensorLevel[] = ["normal", "low", "very_low"];
  return (
    <div>
      <Label className="text-xs">{label}</Label>
      <div className="grid grid-cols-3 gap-1 rounded-xl bg-paper-2 p-1">
        {levels.map((l) => (
          <button
            key={l}
            type="button"
            onClick={() => onChange(l)}
            className={cn("relative h-9 rounded-lg text-xs font-bold transition-colors", value === l ? "text-ink" : "text-ink-3 hover:text-ink-2")}
          >
            {value === l && <motion.span layoutId={`lvl-${label}`} className="absolute inset-0 rounded-lg bg-surface shadow-[var(--shadow-soft)]" />}
            <span className="relative">{t(`diag.opt.${l}` as MessageKey)}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export function DetailsPanel({
  value,
  onChange,
  seasons,
  currentSeason,
}: {
  value: DetailsValue;
  onChange: (v: DetailsValue) => void;
  seasons: string[];
  currentSeason?: string;
}) {
  const { t, n } = useI18n();
  const set = <K extends keyof DetailsValue>(k: K, v: DetailsValue[K]) => onChange({ ...value, [k]: v });

  const tabs: [MenuItem, MenuItem] = [
    { label: t("diag.auto"), value: "auto" },
    { label: t("diag.manual"), value: "manual" },
  ];
  const subTabs: [MenuItem, MenuItem] = [
    { label: t("diag.crop"), value: "crop" },
    { label: t("diag.livestock"), value: "livestock" },
  ];
  const [manualDomain, setManualDomain] = useState<"crop" | "livestock">(value.domain === "livestock" ? "livestock" : "crop");
  const tab = value.domain === "auto" ? tabs[0] : tabs[1];

  const showCrop = value.domain !== "livestock";
  const showLivestock = value.domain !== "crop";
  const symptomKeys = [...(showCrop ? CROP_SYMPTOMS : []), ...(showLivestock ? LIVESTOCK_SYMPTOMS : [])];
  const seasonName = (s: string) => t(`season.${s}` as MessageKey);

  return (
    <div className="space-y-5">
      <Section icon={Stethoscope} title={t("diag.detect")} hint={value.domain === "auto" ? t("diag.autoHint") : undefined}>
        <SubSelectToggle
          tabs={tabs}
          subTabs={subTabs}
          tab={tab}
          setTab={(tb) => set("domain", tb.value === "auto" ? "auto" : manualDomain)}
          subTab={subTabs.find((s) => s.value === manualDomain)!}
          setSubTab={(s) => {
            const d = s.value as "crop" | "livestock";
            setManualDomain(d);
            set("domain", d);
          }}
        />
      </Section>

      <Section icon={HeartPulse} title={t("diag.symptoms")} hint={t("diag.symptomsHint")}>
        <CoolCheckbox
          strike={false}
          className="-mx-2.5 grid"
          todos={symptomKeys.map((k, i) => ({ id: i, title: t(k), checked: value.symptoms.includes(k) }))}
          onToggle={(id) => {
            const k = symptomKeys[id];
            set("symptoms", value.symptoms.includes(k) ? value.symptoms.filter((x) => x !== k) : [...value.symptoms, k]);
          }}
        />
      </Section>

      <Section icon={NotebookPen} title={t("diag.notes")}>
        <Textarea value={value.notes} onChange={(e) => set("notes", e.target.value)} placeholder={t("diag.notesPlaceholder")} rows={3} maxLength={500} />
        <Hint className="text-right tabular-nums">{n(`${value.notes.length}/500`)}</Hint>
      </Section>

      {showLivestock && (
        <section className="border-t border-line pt-5">
          <button type="button" onClick={() => set("sensorOn", !value.sensorOn)} className="flex w-full items-center justify-between text-left">
            <span>
              <span className="flex items-center gap-2 text-[0.95rem] font-bold text-ink">
                <Thermometer className="size-4 text-leaf" /> {t("diag.sensors")}
              </span>
              <span className="mt-0.5 block text-xs text-ink-3">{t("diag.sensorsHint")}</span>
            </span>
            <motion.span animate={{ rotate: value.sensorOn ? 180 : 0 }} className="flex size-8 items-center justify-center rounded-lg bg-paper-2">
              <ChevronDown className="size-4 text-ink-2" />
            </motion.span>
          </button>
          <AnimatePresence initial={false}>
            {value.sensorOn && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className="space-y-4 pt-4">
                  <div>
                    <div className="flex items-center justify-between">
                      <Label className="mb-0 text-xs">{t("diag.temp")}</Label>
                      <span className={cn("font-display text-lg font-semibold tabular-nums", value.sensor.temperature > 40.5 ? "text-brick" : value.sensor.temperature > 39.5 ? "text-amber" : "text-ink")}>
                        {n(value.sensor.temperature.toFixed(1))}°C
                      </span>
                    </div>
                    <input
                      type="range" min={35} max={42} step={0.1}
                      value={value.sensor.temperature}
                      onChange={(e) => set("sensor", { ...value.sensor, temperature: Number(e.target.value) })}
                      className="mt-2 w-full accent-[var(--leaf)]"
                      aria-label={t("diag.temp")}
                    />
                  </div>
                  <LevelPicker label={t("diag.activity")} value={value.sensor.activity} onChange={(v) => set("sensor", { ...value.sensor, activity: v })} />
                  <LevelPicker label={t("diag.feed")} value={value.sensor.feed_intake} onChange={(v) => set("sensor", { ...value.sensor, feed_intake: v })} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      )}

      <section className="border-t border-line pt-5">
        <Label htmlFor="season">{t("diag.season")}</Label>
        <Select id="season" value={value.season} onChange={(e) => set("season", e.target.value)}>
          <option value="">{t("diag.seasonAuto", { s: currentSeason ? seasonName(currentSeason) : "…" })}</option>
          {seasons.map((s) => (
            <option key={s} value={s}>{seasonName(s)}</option>
          ))}
        </Select>
      </section>
    </div>
  );
}
