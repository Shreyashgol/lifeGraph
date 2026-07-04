const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/** Raised for non-2xx responses so callers can render an error state. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function getHeaders(): HeadersInit {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = localStorage.getItem("lifegraph.token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

function handle401(res: Response) {
  if (res.status === 401) {
    localStorage.removeItem("lifegraph.token");
    localStorage.removeItem("lifegraph.user");
    if (!window.location.pathname.startsWith("/login")) {
      window.location.href = "/login";
    }
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    handle401(res);
    throw new ApiError(`GET ${path} failed`, res.status);
  }
  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    handle401(res);
    throw new ApiError(`POST ${path} failed`, res.status);
  }
  return res.json() as Promise<T>;
}
