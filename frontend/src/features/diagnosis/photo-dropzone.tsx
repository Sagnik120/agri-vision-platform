"use client";

import { Camera, ImagePlus, RefreshCw, UploadCloud } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { cn } from "@/lib/utils";
import { useI18n } from "@/providers/language-provider";

const ACCEPT = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 10 * 1024 * 1024;

export function usePreview(file: File | null) {
  const url = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(() => () => void (url && URL.revokeObjectURL(url)), [url]);
  return url;
}

export function Brackets({ className }: { className?: string }) {
  return (
    <>
      {["top-3 left-3 border-t-2 border-l-2 rounded-tl-lg", "top-3 right-3 border-t-2 border-r-2 rounded-tr-lg", "bottom-3 left-3 border-b-2 border-l-2 rounded-bl-lg", "bottom-3 right-3 border-b-2 border-r-2 rounded-br-lg"].map((c) => (
        <span key={c} className={cn("pointer-events-none absolute size-7 border-paper", c, className)} />
      ))}
    </>
  );
}

export function PhotoDropzone({ file, onFile }: { file: File | null; onFile: (f: File) => void }) {
  const { t } = useI18n();
  const preview = usePreview(file);
  const [dragging, setDragging] = useState(false);
  const browseRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);

  const accept = (f?: File | null) => {
    if (!f) return;
    if (!ACCEPT.includes(f.type)) return void toast.error(t("diag.dropHint"));
    if (f.size > MAX_BYTES) return void toast.error(t("diag.dropHint"));
    onFile(f);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        accept(e.dataTransfer.files?.[0]);
      }}
      className={cn(
        "relative aspect-[4/3] w-full overflow-hidden rounded-3xl border-2 border-dashed transition-all duration-300 sm:aspect-square lg:aspect-[4/5]",
        dragging ? "scale-[1.01] border-leaf bg-leaf-50" : preview ? "border-transparent" : "border-line-2 bg-surface/70",
      )}
    >
      <input ref={browseRef} type="file" accept={ACCEPT.join(",")} hidden onChange={(e) => accept(e.target.files?.[0])} />
      <input ref={cameraRef} type="file" accept="image/*" capture="environment" hidden onChange={(e) => accept(e.target.files?.[0])} />

      <AnimatePresence mode="wait">
        {preview ? (
          <motion.div
            key={preview}
            initial={{ opacity: 0, scale: 1.04, filter: "blur(8px)" }}
            animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0"
          >
            {/* eslint-disable-next-line @next/next/no-img-element -- local object URL */}
            <img src={preview} alt="" className="h-full w-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-ink/50 via-transparent to-transparent" />
            <Brackets />
            <button
              type="button"
              onClick={() => browseRef.current?.click()}
              className="absolute bottom-4 left-1/2 inline-flex h-10 -translate-x-1/2 items-center gap-2 rounded-full bg-surface/90 px-4 text-sm font-bold text-ink shadow-lg backdrop-blur transition-transform hover:scale-105"
            >
              <RefreshCw className="size-4" /> {t("diag.change")}
            </button>
          </motion.div>
        ) : (
          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
            <div className="dotted-bg pointer-events-none absolute inset-0 opacity-40" />
            <motion.div
              animate={dragging ? { y: -6, scale: 1.08 } : { y: [0, -6, 0] }}
              transition={dragging ? { type: "spring" } : { duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="relative flex size-20 items-center justify-center rounded-3xl bg-leaf-50 text-leaf"
            >
              {dragging ? <UploadCloud className="size-9" strokeWidth={1.5} /> : <ImagePlus className="size-9" strokeWidth={1.5} />}
            </motion.div>
            <p className="relative mt-5 font-display text-2xl font-medium text-ink">{t("diag.drop")}</p>
            <p className="relative mt-1 text-sm text-ink-3">{t("diag.dropOr")}</p>
            <div className="relative mt-4 flex flex-wrap justify-center gap-2">
              <button type="button" onClick={() => browseRef.current?.click()} className="inline-flex h-11 items-center gap-2 rounded-xl bg-leaf px-5 text-sm font-semibold text-paper transition-colors hover:bg-leaf-700 active:scale-[0.97]">
                <ImagePlus className="size-4" /> {t("diag.browse")}
              </button>
              <button type="button" onClick={() => cameraRef.current?.click()} className="inline-flex h-11 items-center gap-2 rounded-xl border border-line-2 bg-surface px-5 text-sm font-semibold text-ink transition-colors hover:bg-paper-2 active:scale-[0.97]">
                <Camera className="size-4" /> {t("diag.camera")}
              </button>
            </div>
            <p className="relative mt-5 text-xs text-ink-3">{t("diag.dropHint")}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
