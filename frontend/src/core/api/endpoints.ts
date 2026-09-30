import type {
  Diagnosis,
  DiagnosisEvent,
  DiagnosisInput,
  Farmer,
  Health,
  HistoryItem,
  Meta,
  OtpRequestResult,
  Session,
  Stats,
} from "../types";
import { apiUrl, currentToken, rawRequest, request } from "./client";

export const metaApi = {
  health: () => request<Health>("/health"),
  meta: () => request<Meta>("/meta"),
};

export const authApi = {
  requestOtp: (phone: string) =>
    request<OtpRequestResult>("/auth/otp/request", { method: "POST", json: { phone } }),
  verifyOtp: (phone: string, code: string) =>
    request<{ verification_token: string }>("/auth/otp/verify", { method: "POST", json: { phone, code } }),
  signup: (verification_token: string, name: string, pin: string) =>
    request<Session>("/auth/signup", { method: "POST", json: { verification_token, name, pin } }),
  login: (phone: string, pin: string) =>
    request<Session>("/auth/login", { method: "POST", json: { phone, pin } }),
};

export const farmApi = {
  me: () => request<Farmer>("/me"),
  update: (patch: { region?: string }) => request<Farmer>("/me", { method: "PATCH", json: patch }),
  stats: () => request<Stats>("/stats"),
};

export const diagnosisApi = {
  list: () => request<HistoryItem[]>("/diagnoses"),
  get: (id: number) => request<Diagnosis>(`/diagnoses/${id}`),
  imageUrl: (id: number) => `${apiUrl(`/diagnoses/${id}/image`)}?token=${encodeURIComponent(currentToken() ?? "")}`,

  /** Streams real pipeline progress (NDJSON) and calls onEvent for each stage. */
  async run(input: DiagnosisInput, onEvent: (e: DiagnosisEvent) => void, signal?: AbortSignal) {
    const form = new FormData();
    form.append("image", input.image, input.image.name ?? "photo.jpg");
    form.append("domain", input.domain);
    form.append("farmer_text", input.farmerText);
    if (input.sensor) form.append("sensor", JSON.stringify(input.sensor));
    if (input.season) form.append("season", input.season);

    const res = await rawRequest("/diagnoses", { method: "POST", body: form, signal });
    if (!res.body) throw new Error("Streaming not supported");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let nl: number;
      while ((nl = buffer.indexOf("\n")) >= 0) {
        const line = buffer.slice(0, nl).trim();
        buffer = buffer.slice(nl + 1);
        if (line) onEvent(JSON.parse(line) as DiagnosisEvent);
      }
      if (done) break;
    }
  },
};
