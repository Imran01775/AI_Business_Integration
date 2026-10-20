import { parseApiError } from "@sales-agent/shared";
import { NextResponse } from "next/server";

import { backendFetch } from "@/shared/lib/backend-fetch";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    email: string;
    password: string;
    display_name: string;
    locale: string;
  };
  const res = await backendFetch("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = parseApiError(res.status, payload);
    return NextResponse.json(
      { error: { code: err.code, message: err.message, trace_id: err.traceId } },
      { status: res.status },
    );
  }
  return NextResponse.json(payload, { status: 201 });
}
