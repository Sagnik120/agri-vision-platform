"use client";

import { AlertTriangle, BrainCircuit, CheckCircle2, CircleDashed, Cpu, Database, HardDrive, Layers, Server, XCircle } from "lucide-react";

import { ErrorState } from "@/components/feedback/empty-state";
import { Stagger, StaggerItem } from "@/components/motion/reveal";
import { Badge, Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

import { useSystem } from "./api";

function fmtBytes(b: number) {
  if (b < 1024) return `${b} B`;
  const u = ["KB", "MB", "GB"];
  let v = b / 1024;
  let i = 0;
  while (v >= 1024 && i < u.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v.toFixed(v < 10 ? 1 : 0)} ${u[i]}`;
}

function fmtUptime(s: number) {
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  return d ? `${d}d ${h}h` : h ? `${h}h ${m}m` : `${m}m`;
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-line py-3 last:border-0">
      <span className="text-sm font-semibold text-ink-3">{label}</span>
      <span className="text-right text-sm font-bold text-ink">{children}</span>
    </div>
  );
}

function Status({ ok, label }: { ok: boolean | null; label: string }) {
  const Icon = ok === null ? CircleDashed : ok ? CheckCircle2 : XCircle;
  return <Badge tone={ok === null ? "neutral" : ok ? "leaf" : "brick"}><Icon />{label}</Badge>;
}

function Panel({ icon: Icon, title, children }: { icon: typeof Server; title: string; children: React.ReactNode }) {
  return (
    <Card className="h-full p-6">
      <h2 className="flex items-center gap-2.5 font-sans text-lg font-bold">
        <span className="flex size-9 items-center justify-center rounded-xl bg-leaf-50 text-leaf"><Icon className="size-4.5" /></span>
        {title}
      </h2>
      <div className="mt-4">{children}</div>
    </Card>
  );
}

export function SystemView() {
  const { t, n } = useI18n();
  const q = useSystem();
  const s = q.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-medium sm:text-5xl">{t("admin.system.title")}</h1>
        <p className="mt-2 text-ink-2">{t("admin.system.subtitle")}</p>
      </div>

      {q.isError ? (
        <ErrorState message={(q.error as Error).message} onRetry={() => q.refetch()} retryLabel={t("common.retry")} />
      ) : !s ? (
        <div className="grid gap-5 lg:grid-cols-2">{[0, 1, 2, 3].map((i) => <div key={i} className="skeleton h-56 rounded-2xl" />)}</div>
      ) : (
        <>
          {(s.default_admin_password || s.demo_otp) && (
            <div role="alert" className="flex gap-3 rounded-2xl border border-[#f1dfb4] bg-amber-50 px-4 py-3.5 text-sm font-medium text-[#7a5a14]">
              <AlertTriangle className="mt-0.5 size-4 shrink-0" />
              <div className="space-y-1">
                {s.default_admin_password && <p>{t("admin.system.warnPassword")}</p>}
                {s.demo_otp && <p>{t("admin.system.warnOtp")}</p>}
              </div>
            </div>
          )}

          <Stagger inView={false} className="grid gap-5 lg:grid-cols-2">
            <StaggerItem>
              <Panel icon={BrainCircuit} title={t("admin.system.llm")}>
                <Row label={t("set.advisory")}>{s.llm.backend}</Row>
                {s.llm.backend === "local_llm" && (
                  <>
                    <Row label={t("admin.system.model")}><span className="font-mono text-xs">{s.llm.model || "—"}</span></Row>
                    <Row label={t("admin.system.reachable")}>
                      <Status ok={s.llm.reachable} label={s.llm.reachable ? t("set.ready") : s.llm.reachable === false ? t("status.offline") : t("set.notConfigured")} />
                    </Row>
                    {s.llm.latency_ms !== null && <Row label={t("admin.system.latency")}>{n(`${s.llm.latency_ms} ms`)}</Row>}
                  </>
                )}
                <Row label={t("admin.system.gemini")}><Status ok={s.gemini_ready} label={s.gemini_ready ? t("set.ready") : t("set.notConfigured")} /></Row>
                <Row label="RAG">{s.rag_backend}</Row>
              </Panel>
            </StaggerItem>

            <StaggerItem>
              <Panel icon={Cpu} title={t("admin.system.vision")}>
                <Row label={t("set.mode")}>
                  <Badge tone={s.vision.expert_mode === "mock" ? "ochre" : "leaf"}>{s.vision.expert_mode}</Badge>
                </Row>
                <Row label={t("admin.system.moe")}>{s.vision.moe_enabled} · {s.vision.moe_routing}</Row>
                <Row label={t("admin.system.weather")}><Status ok={s.weather_enabled} label={s.weather_enabled ? t("set.ready") : t("admin.system.off")} /></Row>
                <Row label={t("admin.system.otp")}>{s.demo_otp ? t("admin.system.demo") : t("admin.system.sms")}</Row>
              </Panel>
            </StaggerItem>

            <StaggerItem>
              <Panel icon={Layers} title={t("admin.system.models")}>
                <ul className="space-y-2">
                  {s.models.map((m) => (
                    <li key={m.name} className="flex items-center justify-between gap-3 rounded-xl bg-paper-2 px-3 py-2.5">
                      <span className="flex min-w-0 items-center gap-2 text-sm font-semibold text-ink-2">
                        {m.present ? <CheckCircle2 className="size-4 shrink-0 text-leaf" /> : <XCircle className="size-4 shrink-0 text-brick" />}
                        <span className="truncate font-mono text-xs">{m.name}</span>
                      </span>
                      <span className={cn("text-xs font-bold tabular-nums", m.present ? "text-ink-2" : "text-brick")}>
                        {m.present ? n(fmtBytes(m.size_bytes)) : t("admin.system.missing")}
                      </span>
                    </li>
                  ))}
                </ul>
              </Panel>
            </StaggerItem>

            <StaggerItem>
              <Panel icon={Server} title={t("admin.system.server")}>
                <Row label={t("admin.system.uptime")}>{n(fmtUptime(s.api.uptime_s))}</Row>
                <Row label="API">{n(`v${s.api.version}`)}</Row>
                <Row label="Python">{s.api.python}</Row>
                <Row label={t("admin.system.platform")}>{s.api.platform}</Row>
                <Row label={t("admin.system.db")}><span className="flex items-center gap-1.5"><Database className="size-3.5 text-ink-3" />{n(fmtBytes(s.storage.db_bytes))}</span></Row>
                <Row label={t("admin.system.uploads")}>
                  <span className="flex items-center gap-1.5"><HardDrive className="size-3.5 text-ink-3" />{n(`${s.storage.uploads_files} · ${fmtBytes(s.storage.uploads_bytes)}`)}</span>
                </Row>
              </Panel>
            </StaggerItem>
          </Stagger>
        </>
      )}
    </div>
  );
}
