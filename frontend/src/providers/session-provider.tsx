"use client";

import { useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useMemo } from "react";

import { configureApi } from "@/core/api/client";
import type { Farmer, Session } from "@/core/types";
import { storage, useStoredValue } from "@/lib/storage";

const TOKEN_KEY = "agrivision.token";
const FARMER_KEY = "agrivision.farmer";

type Status = "loading" | "authenticated" | "anonymous";

interface SessionContextValue {
  status: Status;
  farmer: Farmer | null;
  signIn: (s: Session) => void;
  signOut: () => void;
  setFarmer: (f: Farmer) => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

/** Explicit NEXT_PUBLIC_API_URL wins; otherwise the API is assumed on port 8000 of whatever host served the page
 *  (localhost, the laptop's LAN IP from a phone, …). */
function defaultApiUrl() {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  if (typeof window === "undefined") return "http://localhost:8000";
  const host = window.location.hostname === "0.0.0.0" ? "localhost" : window.location.hostname;
  return `${window.location.protocol}//${host}:8000`;
}

configureApi({
  baseUrl: defaultApiUrl(),
  getToken: () => storage.get(TOKEN_KEY),
});

function parseFarmer(raw: string | null | undefined): Farmer | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Farmer;
  } catch {
    return null;
  }
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const token = useStoredValue(TOKEN_KEY);
  const farmerRaw = useStoredValue(FARMER_KEY);

  // undefined = still hydrating (server render / first client pass)
  const status: Status = token === undefined ? "loading" : token ? "authenticated" : "anonymous";
  const farmer = useMemo(() => parseFarmer(farmerRaw), [farmerRaw]);

  const signOut = useCallback(() => {
    storage.remove(TOKEN_KEY);
    storage.remove(FARMER_KEY);
    queryClient.clear();
  }, [queryClient]);

  useEffect(() => {
    configureApi({ onUnauthorized: signOut });
  }, [signOut]);

  const setFarmer = useCallback((f: Farmer) => storage.set(FARMER_KEY, JSON.stringify(f)), []);

  const signIn = useCallback(
    (s: Session) => {
      storage.set(FARMER_KEY, JSON.stringify(s.farmer));
      storage.set(TOKEN_KEY, s.token);
    },
    [],
  );

  const value = useMemo(
    () => ({ status, farmer, signIn, signOut, setFarmer }),
    [status, farmer, signIn, signOut, setFarmer],
  );
  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used inside SessionProvider");
  return ctx;
}
