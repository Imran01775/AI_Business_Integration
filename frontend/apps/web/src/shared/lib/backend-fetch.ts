import {
  COOKIE_ACCESS,
  COOKIE_CSRF,
  COOKIE_REFRESH,
  HEADER_CLIENT,
  HEADER_CSRF,
  HEADER_TENANT,
} from "@sales-agent/shared";

import { getBackendUrl } from "@/shared/config/env";

export type BackendFetchInit = RequestInit & {
  tenantId?: string;
  accessToken?: string;
  csrfToken?: string;
};

export function backendUrl(path: string): string {
  const base = getBackendUrl();
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function backendFetch(path: string, init: BackendFetchInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set(HEADER_CLIENT, "web");
  if (init.accessToken) {
    headers.set("Authorization", `Bearer ${init.accessToken}`);
  }
  if (init.tenantId) {
    headers.set(HEADER_TENANT, init.tenantId);
  }
  const method = (init.method ?? "GET").toUpperCase();
  if (!["GET", "HEAD", "OPTIONS"].includes(method) && init.csrfToken) {
    headers.set(HEADER_CSRF, init.csrfToken);
  }
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(backendUrl(path), { ...init, headers });
}

export const AUTH_COOKIES = {
  access: COOKIE_ACCESS,
  refresh: COOKIE_REFRESH,
  csrf: COOKIE_CSRF,
} as const;
