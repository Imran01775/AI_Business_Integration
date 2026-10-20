import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIES, backendUrl } from "@/shared/lib/backend-fetch";
import { refreshSessionIfNeeded } from "@/shared/lib/auth-cookies";

async function proxy(request: Request, path: string[]) {
  const targetPath = `/${path.join("/")}`;
  const url = new URL(request.url);
  const backend = `${backendUrl(targetPath)}${url.search}`;

  const jar = await cookies();
  let access = jar.get(AUTH_COOKIES.access)?.value;
  if (!access) {
    access = await refreshSessionIfNeeded();
  }

  const headers = new Headers(request.headers);
  headers.delete("host");
  if (access) {
    headers.set("Authorization", `Bearer ${access}`);
  }
  const csrf = jar.get(AUTH_COOKIES.csrf)?.value;
  if (csrf) {
    headers.set("X-CSRF-Token", csrf);
  }
  const tenant = jar.get("tenant_id")?.value;
  if (tenant) {
    headers.set("X-Tenant-Id", tenant);
  }
  headers.set("X-Client", "web");

  const init: RequestInit = {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
  };

  const res = await fetch(backend, init);
  const responseHeaders = new Headers(res.headers);
  responseHeaders.delete("content-encoding");
  return new NextResponse(res.body, { status: res.status, headers: responseHeaders });
}

export async function GET(request: Request, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(request, path);
}

export async function POST(request: Request, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(request, path);
}

export async function PATCH(request: Request, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(request, path);
}

export async function DELETE(request: Request, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(request, path);
}
