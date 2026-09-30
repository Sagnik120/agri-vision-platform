/**
 * Minimal fetch client. The session token is injected by the host app
 * (web: localStorage, mobile later: SecureStore) via configureApi().
 */

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface ApiConfig {
  baseUrl: string;
  getToken: () => string | null;
  onUnauthorized?: () => void;
}

const config: ApiConfig = {
  baseUrl: "http://localhost:8000",
  getToken: () => null,
};

export function configureApi(next: Partial<ApiConfig>) {
  Object.assign(config, next);
}

export function apiUrl(path: string) {
  return `${config.baseUrl}/api/v1${path}`;
}

export function currentToken() {
  return config.getToken();
}

async function toApiError(res: Response): Promise<ApiError> {
  let message = `Request failed (${res.status})`;
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") message = body.detail;
    // FastAPI validation errors: [{ msg: "Value error, Enter a valid..." }]
    else if (Array.isArray(body?.detail) && body.detail[0]?.msg) {
      message = String(body.detail[0].msg).replace(/^Value error, /, "");
    }
  } catch {
    /* non-JSON error body */
  }
  if (res.status === 401) config.onUnauthorized?.();
  return new ApiError(message, res.status);
}

export async function rawRequest(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const token = config.getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let res: Response;
  try {
    res = await fetch(apiUrl(path), { ...init, headers });
  } catch {
    throw new ApiError("Cannot reach the Agri-Vision server. Is it running?", 0);
  }
  if (!res.ok) throw await toApiError(res);
  return res;
}

export async function request<T>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
  const { json, ...rest } = init;
  const headers = new Headers(rest.headers);
  if (json !== undefined) headers.set("Content-Type", "application/json");
  const res = await rawRequest(path, {
    ...rest,
    headers,
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  return res.json() as Promise<T>;
}
