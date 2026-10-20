import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { backendFetch } from "@/shared/lib/backend-fetch";
import { clearAuthCookies, readAuthCookies } from "@/shared/lib/auth-cookies";

export async function POST() {
  const auth = await readAuthCookies();
  if (auth.access) {
    await backendFetch("/api/v1/auth/logout", {
      method: "POST",
      accessToken: auth.access,
      csrfToken: auth.csrf,
    });
  }
  const jar = await cookies();
  clearAuthCookies(jar);
  return new NextResponse(null, { status: 204 });
}
