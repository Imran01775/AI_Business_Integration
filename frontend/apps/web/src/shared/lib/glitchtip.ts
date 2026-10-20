import * as Sentry from "@sentry/nextjs";

export function initGlitchtipBrowser() {
  const dsn = process.env.NEXT_PUBLIC_GLITCHTIP_DSN;
  if (!dsn) {
    return;
  }
  Sentry.init({
    dsn,
    tracesSampleRate: 0.1,
    environment: process.env.NEXT_PUBLIC_APP_ENV ?? "development",
  });
}

export function captureApiError(error: unknown, traceId?: string) {
  if (traceId) {
    Sentry.setTag("trace_id", traceId);
  }
  Sentry.captureException(error);
}
