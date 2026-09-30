"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import { diagnosisApi } from "@/core/api/endpoints";
import type { Diagnosis, DiagnosisEvent, DiagnosisInput, Domain, Route } from "@/core/types";
import { queryKeys } from "@/features/farm/queries";

export type StepId = "upload" | "vision" | "gate" | "knowledge" | "cloud" | "save";
export type StepStatus = "pending" | "active" | "done" | "error";

export interface RunState {
  phase: "idle" | "running" | "result" | "rejected" | "error";
  steps: Record<StepId, StepStatus>;
  domain?: Domain;
  prediction?: string;
  route?: Route;
  confidence?: number;
  result?: Diagnosis;
  message?: string;
}

const INITIAL: RunState = {
  phase: "idle",
  steps: { upload: "pending", vision: "pending", gate: "pending", knowledge: "pending", cloud: "pending", save: "pending" },
};

/** Minimum time each real pipeline event stays on screen, so fast (mock) runs remain readable. */
const PACE_MS = 480;

export function useDiagnosisRun() {
  const queryClient = useQueryClient();
  const [state, setState] = useState<RunState>(INITIAL);
  const queue = useRef<DiagnosisEvent[]>([]);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abort = useRef<AbortController | null>(null);

  const apply = useCallback(
    (e: DiagnosisEvent) =>
      setState((s) => {
        const steps = { ...s.steps };
        switch (e.type) {
          case "stage": {
            steps[e.stage] = e.status;
            if (e.stage === "vision" && e.status === "done") steps.gate = "active";
            if (e.stage === "gate" && e.route === "local") {
              steps.knowledge = "pending";
              steps.cloud = "pending";
              steps.save = "active";
            }
            if (e.stage === "cloud" && e.status === "done") steps.save = "active";
            return {
              ...s,
              steps,
              domain: e.domain ?? s.domain,
              prediction: e.prediction ?? s.prediction,
              route: e.route ?? s.route,
              confidence: e.confidence ?? s.confidence,
            };
          }
          case "result":
            steps.save = "done";
            return { ...s, steps, phase: "result", result: e.data };
          case "rejected":
            return { ...s, steps, phase: "rejected", message: e.reason };
          case "error":
            return { ...s, steps, phase: "error", message: e.message };
        }
      }),
    [],
  );

  const pump = useCallback(() => {
    if (timer.current) return;
    const tick = () => {
      const next = queue.current.shift();
      if (!next) {
        timer.current = null;
        return;
      }
      apply(next);
      timer.current = setTimeout(tick, next.type === "stage" ? PACE_MS : 0);
    };
    tick();
  }, [apply]);

  const push = useCallback(
    (e: DiagnosisEvent) => {
      queue.current.push(e);
      pump();
    },
    [pump],
  );

  const start = useCallback(
    async (input: DiagnosisInput) => {
      abort.current?.abort();
      abort.current = new AbortController();
      queue.current = [];
      setState({ ...INITIAL, phase: "running", steps: { ...INITIAL.steps, upload: "active" } });
      setTimeout(() => setState((s) => ({ ...s, steps: { ...s.steps, upload: "done" } })), 350);
      try {
        await diagnosisApi.run(input, push, abort.current.signal);
        queryClient.invalidateQueries({ queryKey: queryKeys.history });
        queryClient.invalidateQueries({ queryKey: queryKeys.stats });
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        push({ type: "error", message: (err as Error).message });
      }
    },
    [push, queryClient],
  );

  const reset = useCallback(() => {
    abort.current?.abort();
    queue.current = [];
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    setState(INITIAL);
  }, []);

  useEffect(() => () => abort.current?.abort(), []);

  return { state, start, reset };
}
