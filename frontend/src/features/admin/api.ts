"use client";

import { useQuery } from "@tanstack/react-query";

import { ApiError, apiUrl } from "@/core/api/client";
import type { Diagnosis, Domain, Route } from "@/core/types";
import { storage, useStoredValue } from "@/lib/storage";

/** Admin sessions are kept apart from farmer sessions (separate token, separate login). */
const ADMIN_TOKEN_KEY = "agrivision.admin.token";
const ADMIN_USER_KEY = "agrivision.admin.user";

export interface AdminCheck {
  id: number;
  created_at: string;
  farm_id: string;
  farmer_name: string;
  region: string | null;
  domain: Domain;
  route: Route;
  condition: string;
  certainty: string | null;
  confidence: number;
  visual_confidence: number;
  healthy: boolean;
  summary: string;
  farmer_text: string;
  has_sensor: boolean;
  has_image: boolean;
}

export interface PeriodSummary {
  checks: number; crop: number; livestock: number; healthy: number; attention: number; local: number; cloud: number;
  avg_confidence: number; low_confidence: number; active_farmers: number; with_notes: number; with_sensor: number;
}

export interface Overview {
  days: number;
  generated_at: string;
  totals: { farmers: number; new_farmers: number; all_time_checks: number };
  current: PeriodSummary;
  previous: PeriodSummary;
  daily: { date: string; crop: number; livestock: number; attention: number }[];
  top_conditions: { condition: string; domain: Domain; count: number; avg_confidence: number; cloud: number; healthy: boolean }[];
  regions: { region: string; farmers: number; checks: number; attention: number }[];
  confidence_buckets: number[];
  hours_ist: number[];
  alerts: { condition: string; region: string; count: number }[];
  recent: AdminCheck[];
}

export interface AdminFarmer {
  farm_id: string; name: string; phone: string; region: string | null; created_at: string;
  checks: number; crop: number; livestock: number; attention: number; last_check_at: string | null;
}

export interface SystemInfo {
  api: { version: string; uptime_s: number; python: string; platform: string };
  vision: { expert_mode: string; moe_enabled: string; moe_routing: string };
  llm: { backend: string; model: string; configured: boolean; reachable: boolean | null; latency_ms: number | null };
  gemini_ready: boolean;
  rag_backend: string;
  weather_enabled: boolean;
  demo_otp: boolean;
  default_admin_password: boolean;
  storage: { db_bytes: number; uploads_files: number; uploads_bytes: number };
  models: { name: string; present: boolean; size_bytes: number }[];
}

export const adminToken = () => storage.get(ADMIN_TOKEN_KEY);

export function adminSignOut() {
  storage.remove(ADMIN_TOKEN_KEY);
  storage.remove(ADMIN_USER_KEY);
}

async function adminFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const token = adminToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let res: Response;
  try {
    res = await fetch(apiUrl(`/admin${path}`), { ...init, headers });
  } catch {
    throw new ApiError("Cannot reach the Agri-Vision server. Is it running?", 0);
  }
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") message = body.detail;
    } catch {
      /* non-JSON */
    }
    if (res.status === 401 && token) adminSignOut();
    throw new ApiError(message, res.status);
  }
  return res;
}

const get = <T,>(path: string) => adminFetch(path).then((r) => r.json() as Promise<T>);

export const adminApi = {
  async login(username: string, password: string) {
    const res = await adminFetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const s = (await res.json()) as { token: string; username: string };
    storage.set(ADMIN_USER_KEY, s.username);
    storage.set(ADMIN_TOKEN_KEY, s.token);
    return s;
  },
  overview: (days: number) => get<Overview>(`/overview?days=${days}`),
  farmers: () => get<AdminFarmer[]>("/farmers"),
  farmer: (id: string) => get<AdminFarmer & { checks: AdminCheck[] }>(`/farmers/${encodeURIComponent(id)}`),
  checks: () => get<AdminCheck[]>("/diagnoses"),
  check: (id: number) => get<Diagnosis & { farmer_name: string; region: string | null; farm_id: string }>(`/diagnoses/${id}`),
  system: () => get<SystemInfo>("/system"),
  imageUrl: (id: number) => `${apiUrl(`/admin/diagnoses/${id}/image`)}?token=${encodeURIComponent(adminToken() ?? "")}`,
  async downloadCsv() {
    const res = await adminFetch("/export.csv");
    const blob = await res.blob();
    const name = /filename="(.+?)"/.exec(res.headers.get("Content-Disposition") ?? "")?.[1] ?? "agrivision-checks.csv";
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: name });
    a.click();
    URL.revokeObjectURL(a.href);
  },
};

export function useAdminSession() {
  const token = useStoredValue(ADMIN_TOKEN_KEY);
  const user = useStoredValue(ADMIN_USER_KEY);
  const status = token === undefined ? "loading" : token ? "authenticated" : "anonymous";
  return { status, user: user ?? "" } as const;
}

export const useOverview = (days: number) =>
  useQuery({ queryKey: ["admin", "overview", days], queryFn: () => adminApi.overview(days), refetchInterval: 60_000 });
export const useAdminFarmers = () => useQuery({ queryKey: ["admin", "farmers"], queryFn: adminApi.farmers });
export const useAdminFarmer = (id: string) => useQuery({ queryKey: ["admin", "farmer", id], queryFn: () => adminApi.farmer(id) });
export const useAdminChecks = () => useQuery({ queryKey: ["admin", "checks"], queryFn: adminApi.checks, refetchInterval: 60_000 });
export const useAdminCheck = (id: number) =>
  useQuery({ queryKey: ["admin", "check", id], queryFn: () => adminApi.check(id), enabled: Number.isFinite(id) });
export const useSystem = () => useQuery({ queryKey: ["admin", "system"], queryFn: adminApi.system, refetchInterval: 30_000 });
