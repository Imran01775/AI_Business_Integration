import { parseApiError } from "@sales-agent/shared";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { backendFetch } from "@/shared/lib/backend-fetch";
import { readAuthCookies, setAuthCookies } from "@/shared/lib/auth-cookies";

export async function POST() {
  const auth = await readAuthCookies();
  if (!auth.refresh) {
    return NextResponse.json({ error: { code: "auth.unauthenticated" } }, { status: 401 });
  }
  const res = await backendFetch("/api/v1/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: auth.refresh }),
  });
  const payload = await res.json();
  if (!res.ok) {
    const err = parseApiError(res.status, payload);
    return NextResponse.json(
      { error: { code: err.code, message: err.message } },
      { status: res.status },
    );
  }
  const data = payload as { access_token: string; refresh_token: string };
  const jar = await cookies();
  setAuthCookies(jar, { access: data.access_token, refresh: data.refresh_token });
  return NextResponse.json({ ok: true });
}
