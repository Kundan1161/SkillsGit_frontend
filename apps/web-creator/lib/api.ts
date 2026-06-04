/**
 * Placeholder fetch wrapper. This will be replaced by the generated
 * client from `@skillsgit/api-client` after `pnpm codegen` runs against
 * the FastAPI OpenAPI schema. Until then, all callers should use this
 * helper so swapping the implementation is a one-line change.
 *
 * Mirrors the marketplace wrapper so both apps speak to the same backend.
 */

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ApiError = {
  status: number;
  code: string;
  message: string;
  details?: unknown;
};

async function request<T>(
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
  path: string,
  body?: unknown,
  init?: RequestInit,
): Promise<T> {
  const url = `${API_URL}${path}`;
  const headers = new Headers(init?.headers);
  if (body !== undefined && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }

  const res = await fetch(url, {
    method,
    credentials: "include",
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    ...init,
  });

  if (!res.ok) {
    let parsed: unknown = undefined;
    try {
      parsed = await res.json();
    } catch {
      // ignore — non-JSON error body
    }
    const err: ApiError = {
      status: res.status,
      code:
        (parsed as { code?: string })?.code ??
        `http_${res.status}`,
      message:
        (parsed as { message?: string })?.message ??
        res.statusText,
      details: parsed,
    };
    throw err;
  }

  // 204 No Content
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string, init?: RequestInit) =>
    request<T>("GET", path, undefined, init),
  post: <T>(path: string, body?: unknown, init?: RequestInit) =>
    request<T>("POST", path, body, init),
  put: <T>(path: string, body?: unknown, init?: RequestInit) =>
    request<T>("PUT", path, body, init),
  patch: <T>(path: string, body?: unknown, init?: RequestInit) =>
    request<T>("PATCH", path, body, init),
  delete: <T>(path: string, init?: RequestInit) =>
    request<T>("DELETE", path, undefined, init),
};
