"use client";

import { useSyncExternalStore } from "react";

type Area = "local" | "session";

function area(a: Area): Storage | null {
  try {
    return typeof window === "undefined" ? null : a === "local" ? window.localStorage : window.sessionStorage;
  } catch {
    return null; // private mode / blocked storage
  }
}

const listeners = new Set<() => void>();
const notify = () => listeners.forEach((l) => l());

function subscribe(cb: () => void) {
  listeners.add(cb);
  window.addEventListener("storage", cb); // other tabs
  return () => {
    listeners.delete(cb);
    window.removeEventListener("storage", cb);
  };
}

/** Storage wrapper that never throws and notifies subscribed components on change. */
export const storage = {
  get(key: string, a: Area = "local"): string | null {
    try {
      return area(a)?.getItem(key) ?? null;
    } catch {
      return null;
    }
  },
  set(key: string, value: string, a: Area = "local") {
    try {
      area(a)?.setItem(key, value);
    } catch {
      /* ignore */
    }
    notify();
  },
  remove(key: string, a: Area = "local") {
    try {
      area(a)?.removeItem(key);
    } catch {
      /* ignore */
    }
    notify();
  },
};

/**
 * Reads a stored value reactively and hydration-safely:
 * the server (and the hydration pass) see `undefined`, the client then sees the real value.
 */
export function useStoredValue(key: string, a: Area = "local"): string | null | undefined {
  return useSyncExternalStore(
    subscribe,
    () => storage.get(key, a),
    () => undefined,
  );
}
