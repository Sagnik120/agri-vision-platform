"use client";

import { Camera, History, RotateCcw, ScanSearch, TriangleAlert } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";

import { StatusButton } from "@/components/jyotirmoydas/status-button";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { translate } from "@/core/i18n";
import { useMeta } from "@/features/farm/queries";
import { useI18n } from "@/providers/language-provider";

import { DEFAULT_DETAILS, DetailsPanel, type DetailsValue } from "./details-panel";
import { Brackets, PhotoDropzone, usePreview } from "./photo-dropzone";
import { PipelineTimeline } from "./pipeline-timeline";
import { ResultView } from "./result-view";
import { useDiagnosisRun } from "./use-diagnosis-run";

const fade = {
  initial: { opacity: 0, y: 16, filter: "blur(6px)" },
  animate: { opacity: 1, y: 0, filter: "blur(0px)" },
  exit: { opacity: 0, y: -12, filter: "blur(6px)" },
  transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] as const },
};

/** Symptom chips are sent in English so the backend keyword matcher understands them. */
function buildFarmerText(d: DetailsValue) {
  const sym = d.symptoms.map((k) => translate("en", k));
  return [d.notes.trim(), sym.length ? `Symptoms: ${sym.join(", ")}` : ""].filter(Boolean).join(". ");
}

function ScanningPhoto({ file }: { file: File }) {
  const url = usePreview(file);
  return (
    <div className="relative aspect-[4/3] overflow-hidden rounded-3xl bg-ink sm:aspect-square lg:aspect-[4/5]">
      {url && (
        // eslint-disable-next-line @next/next/no-img-element -- local object URL
        <img src={url} alt="" className="h-full w-full object-cover opacity-90" />
      )}
      <div className="absolute inset-0 [background-image:linear-gradient(var(--leaf)_1px,transparent_1px),linear-gradient(90deg,var(--leaf)_1px,transparent_1px)] [background-size:32px_32px] opacity-15" />
      <div className="absolute inset-x-0 top-0 h-full">
        <div className="h-[12%] w-full animate-scan bg-gradient-to-b from-transparent via-ochre/40 to-transparent">
          <div className="absolute bottom-1/2 h-[2px] w-full bg-ochre shadow-[0_0_16px_var(--ochre)]" />
        </div>
      </div>
      <Brackets />
    </div>
  );
}

export function DiagnoseView() {
  const { t, text } = useI18n();
  const meta = useMeta();
  const { state, start, reset } = useDiagnosisRun();
  const [file, setFile] = useState<File | null>(null);
  const [details, setDetails] = useState<DetailsValue>(DEFAULT_DETAILS);
  const [revealedId, setRevealedId] = useState<number | null>(null);
  const resultId = state.phase === "result" ? state.result?.id : undefined;
  const showResult = resultId !== undefined && revealedId === resultId;

  // Let the final "saved" tick land before swapping to the result.
  useEffect(() => {
    if (resultId === undefined) return;
    const id = setTimeout(() => setRevealedId(resultId), 750);
    return () => clearTimeout(id);
  }, [resultId]);

  const analyze = () => {
    if (!file) return;
    start({
      image: file,
      domain: details.domain,
      farmerText: buildFarmerText(details),
      sensor: details.domain !== "crop" && details.sensorOn ? details.sensor : null,
      season: details.season || null,
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const again = () => {
    reset();
    setFile(null);
    setDetails(DEFAULT_DETAILS);
  };

  const view =
    state.phase === "idle" ? "compose"
    : state.phase === "result" && showResult ? "result"
    : state.phase === "rejected" || state.phase === "error" ? "problem"
    : "running";

  return (
    <div>
      <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-medium sm:text-5xl">{t("diag.title")}</h1>
          <p className="mt-2 text-ink-2">{t("diag.subtitle")}</p>
        </div>
        {view === "result" && (
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} className="flex gap-2">
            <Button variant="outline" href="/history"><History /> {t("nav.history")}</Button>
            <Button onClick={again}><Camera /> {t("diag.again")}</Button>
          </motion.div>
        )}
      </div>

      <AnimatePresence mode="wait">
        {view === "compose" && (
          <motion.div key="compose" {...fade} className="grid gap-6 lg:grid-cols-[1fr_1.05fr]">
            <PhotoDropzone file={file} onFile={setFile} />
            <Card className="flex flex-col p-6 sm:p-7">
              <DetailsPanel value={details} onChange={setDetails} seasons={meta.data?.seasons ?? ["kharif", "rabi", "zaid"]} currentSeason={meta.data?.current_season} />
              <div className="mt-7 border-t border-line pt-6">
                <StatusButton
                  onClick={analyze}
                  disabled={!file}
                  radius="lg"
                  className="h-14 w-full text-lg"
                  icon={<ScanSearch className="size-5" />}
                >
                  {file ? t("diag.analyze") : t("diag.needPhoto")}
                </StatusButton>
              </div>
            </Card>
          </motion.div>
        )}

        {view === "running" && file && (
          <motion.div key="running" {...fade} className="grid items-start gap-6 lg:grid-cols-[1fr_1.05fr]">
            <ScanningPhoto file={file} />
            <Card className="p-6 sm:p-8">
              <StatusButton variant="loading" radius="lg" className="pointer-events-none mb-8 w-full" text={{ loading: t("diag.analyzing") }}>
                {t("diag.analyzing")}
              </StatusButton>
              <PipelineTimeline state={state} />
            </Card>
          </motion.div>
        )}

        {view === "problem" && (
          <motion.div key="problem" {...fade} className="mx-auto max-w-lg">
            <Card className="p-8 text-center">
              <motion.div
                initial={{ scale: 0.6, rotate: -10 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 15 }}
                className="mx-auto flex size-16 items-center justify-center rounded-2xl bg-amber-50 text-amber"
              >
                <TriangleAlert className="size-8" />
              </motion.div>
              <h2 className="mt-5 text-3xl font-medium">{state.phase === "rejected" ? t("diag.rejectedTitle") : t("diag.errorTitle")}</h2>
              <p className="mt-3 leading-relaxed text-ink-2">{state.message && text(state.message)}</p>
              <div className="mt-7 flex justify-center gap-2">
                <Button variant="outline" onClick={() => reset()}><RotateCcw /> {t("common.retry")}</Button>
                <Button onClick={again}><Camera /> {t("diag.retake")}</Button>
              </div>
            </Card>
          </motion.div>
        )}

        {view === "result" && state.result && (
          <motion.div key="result" {...fade}>
            <ResultView d={state.result} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
