"use client";

import { useQuery } from "@tanstack/react-query";

import { diagnosisApi, farmApi, metaApi } from "@/core/api/endpoints";

export const queryKeys = {
  me: ["me"] as const,
  stats: ["stats"] as const,
  history: ["history"] as const,
  diagnosis: (id: number) => ["diagnosis", id] as const,
  meta: ["meta"] as const,
};

export const useStats = () => useQuery({ queryKey: queryKeys.stats, queryFn: farmApi.stats });
export const useHistory = () => useQuery({ queryKey: queryKeys.history, queryFn: diagnosisApi.list });
export const useDiagnosis = (id: number) =>
  useQuery({ queryKey: queryKeys.diagnosis(id), queryFn: () => diagnosisApi.get(id), enabled: Number.isFinite(id) });
export const useMeta = () => useQuery({ queryKey: queryKeys.meta, queryFn: metaApi.meta, staleTime: Infinity });
export const useMe = (enabled = true) => useQuery({ queryKey: queryKeys.me, queryFn: farmApi.me, enabled });
