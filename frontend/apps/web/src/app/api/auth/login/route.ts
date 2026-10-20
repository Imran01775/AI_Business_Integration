import { parseApiError } from "@sales-agent/shared";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { backendFetch } from "@/shared/lib/backend-fetch";
import { setAuthCookies } from "@/shared/lib/auth-cookies";

export async function POST(request: Request) {
  const body = (await request.json()) as { email: string; password: string };
  const res = await backendFetch("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email: body.email,
      password: body.password,
      client_type: "mobile",
    }),
  });
  const payload = await res.json();
  if (!res.ok) {
    const err = parseApiError(res.status, payload);
    return NextResponse.json(
      { error: { code: err.code, message: err.message, trace_id: err.traceId } },
      { status: res.status },
    );
  }
  const data = payload as { access_token: string; refresh_token: string };
  const jar = await cookies();
  setAuthCookies(jar, { access: data.access_token, refresh: data.refresh_token });
  return NextResponse.json({ ok: true });
}
