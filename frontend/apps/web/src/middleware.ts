import createMiddleware from "next-intl/middleware";
import { type NextRequest, NextResponse } from "next/server";

import { COOKIE_ACCESS } from "@sales-agent/shared";

import { routing } from "./i18n/routing";

const intlMiddleware = createMiddleware(routing);

const authPaths = ["/login", "/register", "/verify-email", "/forgot-password", "/reset-password"];

function stripLocale(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length > 0 && routing.locales.includes(segments[0] as "en" | "bn")) {
    return `/${segments.slice(1).join("/")}` || "/";
  }
  return pathname;
}

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const bare = stripLocale(pathname);
  const isAuthPage = authPaths.some((p) => bare === p || bare.startsWith(`${p}/`));
  const isProtected =
    bare.startsWith("/seller") ||
    bare.startsWith("/admin") ||
    bare.startsWith("/settings") ||
    bare.startsWith("/onboarding");

  const hasSession = Boolean(request.cookies.get(COOKIE_ACCESS)?.value);

  if (isProtected && !hasSession) {
    const locale = pathname.split("/")[1] ?? routing.defaultLocale;
    const login = new URL(`/${locale}/login`, request.url);
    login.searchParams.set("next", pathname);
    return NextResponse.redirect(login);
  }

  if (isAuthPage && hasSession) {
    const locale = pathname.split("/")[1] ?? routing.defaultLocale;
    return NextResponse.redirect(new URL(`/${locale}/seller`, request.url));
  }

  return intlMiddleware(request);
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
