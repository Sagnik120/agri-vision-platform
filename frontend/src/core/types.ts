/**
 * API contract types. Mirrors src/api on the backend.
 * core/ is platform-free (no Next.js, no DOM) so the future mobile app can reuse it.
 */

export type Domain = "crop" | "livestock";
export type DomainChoice = Domain | "auto";
export type Route = "local" | "cloud";

export interface Farmer {
  farm_id: string;
  phone: string;
  name: string;
  region: string | null;
  created_at: string;
}

export interface Session {
  token: string;
  farmer: Farmer;
}

export interface OtpRequestResult {
  sent: boolean;
  expires_in: number;
  registered: boolean;
  demo_otp: string | null;
}

export interface Health {
  status: "ok";
  expert_mode: string;
  advisory_backend: string;
  cloud_ready: boolean;
}

export interface Meta {
  regions: string[];
  seasons: string[];
  current_season: string;
  voice_enabled: boolean;
  demo_otp: boolean;
}

export interface Stats {
  total: number;
  crop: number;
  livestock: number;
  healthy: number;
  needs_attention: number;
  offline: number;
  cloud: number;
  last_check_at: string | null;
}

/** Values accepted by src/zone1_edge/multimodal/sensor_expert.py */
export type SensorLevel = "normal" | "low" | "very_low";

export interface SensorReading {
  temperature: number;
  activity: SensorLevel;
  feed_intake: SensorLevel;
}

export interface HistoryItem {
  id: number;
  created_at: string;
  domain: Domain;
  route: Route;
  condition: string;
  certainty: string | null;
  confidence: number;
  summary: string;
  farmer_text?: string;
  has_image: boolean;
}

export interface Prediction {
  label: string;
  confidence: number;
}

export interface Diagnosis {
  id: number;
  created_at: string;
  domain: Domain;
  route: Route;
  prediction: string | null;
  condition: string;
  certainty: string | null;
  confidence: number;
  visual_confidence: number;
  evidence_agreement?: "high" | "medium" | "low" | null;
  summary: string;
  actions: string[];
  warning: string;
  safety_note?: string;
  top_predictions: Prediction[];
  reason?: string;
  context?: { season?: string | null; region?: string | null; note?: string | null };
  quality_flag?: "ok" | "warn";
  vision_backend?: string;
  advisory_backend?: string;
  farmer_text: string;
  expert_consultation_recommended?: boolean;
  citations: string[];
  citation_check?: { cited_doc_ids?: string[]; farm_history_refs?: string[]; citations_valid?: boolean };
  weather?: {
    source?: string;
    temperature_c?: number;
    relative_humidity_pct?: number;
    precipitation_last_7d_mm?: number;
  } | null;
  has_image: boolean;
}

/** Hindi advisory text from GET /diagnoses/{id}/translation (IndicTrans2, cached server-side). */
export type Translation =
  | { available: true; summary: string; warning: string; safety_note: string; context_note: string; actions: string[]; model: string }
  | { available: false; reason: string };

export type PipelineStage = "vision" | "gate" | "knowledge" | "cloud";

export type DiagnosisEvent =
  | { type: "stage"; stage: PipelineStage; status: "active" | "done" | "error"; domain?: Domain; prediction?: string; route?: Route; confidence?: number }
  | { type: "rejected"; reason: string }
  | { type: "error"; message: string }
  | { type: "result"; data: Diagnosis };

export interface DiagnosisInput {
  image: Blob & { name?: string };
  domain: DomainChoice;
  farmerText: string;
  sensor?: SensorReading | null;
  season?: string | null;
}
