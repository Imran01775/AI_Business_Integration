import { cookies } from "next/headers";
import type { ResponseCookies } from "next/dist/compiled/@edge-runtime/cookies";

import { AUTH_COOKIES, backendFetch } from "@/shared/lib/backend-fetch";

const SECURE = process.env.NODE_ENV === "production";

export async function readAuthCookies() {
  const jar = await cookies();
  return {
    access: jar.get(AUTH_COOKIES.access)?.value,
    refresh: jar.get(AUTH_COOKIES.refresh)?.value,
    csrf: jar.get(AUTH_COOKIES.csrf)?.value,
  };
}

export function setAuthCookies(store: ResponseCookies, tokens: { access: string; refresh: string; csrf?: string }) {
  store.set(AUTH_COOKIES.access, tokens.access, {
    httpOnly: true,
    secure: SECURE,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60,
  });
  store.set(AUTH_COOKIES.refresh, tokens.refresh, {
    httpOnly: true,
    secure: SECURE,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
  if (tokens.csrf) {
    store.set(AUTH_COOKIES.csrf, tokens.csrf, {
      httpOnly: false,
      secure: SECURE,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 30,
    });
  }
}

export function clearAuthCookies(store: ResponseCookies) {
  for (const name of Object.values(AUTH_COOKIES)) {
    store.set(name, "", { path: "/", maxAge: 0 });
  }
}

export async function refreshSessionIfNeeded(): Promise<string | undefined> {
  const { access, refresh } = await readAuthCookies();
  if (access) {
    return access;
  }
  if (!refresh) {
    return undefined;
  }
  const res = await backendFetch("/api/v1/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) {
    return undefined;
  }
  const data = (await res.json()) as { access_token: string; refresh_token: string };
  const jar = await cookies();
  setAuthCookies(jar, { access: data.access_token, refresh: data.refresh_token });
  return data.access_token;
}
