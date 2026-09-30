"use client";

import { useCallback, useState } from "react";

export type ActionState = "idle" | "loading" | "success" | "error";

/** Drives StatusButton: idle → loading → success | error (error resets after a moment). */
export function useActionStatus() {
  const [state, setState] = useState<ActionState>("idle");
  const run = useCallback(async <T,>(fn: () => Promise<T>): Promise<T | undefined> => {
    setState("loading");
    try {
      const r = await fn();
      setState("success");
      return r;
    } catch (e) {
      setState("error");
      setTimeout(() => setState("idle"), 1600);
      throw e;
    }
  }, []);
  const variant = state === "idle" ? undefined : state;
  return { state, variant, run, reset: () => setState("idle") } as const;
}
