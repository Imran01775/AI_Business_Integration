import createClient from "openapi-fetch";

import {
  COOKIE_CSRF,
  HEADER_CLIENT,
  HEADER_CSRF,
  HEADER_TENANT,
  HEADER_TRACE,
} from "@sales-agent/shared";

import type { paths } from "./generated/schema";
export type ApiClient = ReturnType<typeof createApiClient>;

export type ApiClientOptions = {
  baseUrl: string;
  getAccessToken?: () => string | undefined;
  getCsrfToken?: () => string | undefined;
  getTenantId?: () => string | undefined;
  getTraceId?: () => string;
  clientType?: "web" | "mobile";
};

export function createApiClient(options: ApiClientOptions) {
  const client = createClient<paths>({ baseUrl: options.baseUrl });

  client.use({
    async onRequest({ request }) {
      const headers = new Headers(request.headers);
      headers.set(HEADER_CLIENT, options.clientType ?? "web");
      const traceId = options.getTraceId?.();
      if (traceId) {
        headers.set(HEADER_TRACE, traceId);
      }
      const tenantId = options.getTenantId?.();
      if (tenantId) {
        headers.set(HEADER_TENANT, tenantId);
      }
      const token = options.getAccessToken?.();
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      const method = request.method.toUpperCase();
      if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
        const csrf = options.getCsrfToken?.();
        if (csrf) {
          headers.set(HEADER_CSRF, csrf);
        }
      }
      return new Request(request, { headers });
    },
  });

  return client;
}

export { COOKIE_CSRF };
