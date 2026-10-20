"use client";

import { errorMessageKey } from "@sales-agent/i18n";
import { ApiError } from "@sales-agent/shared";
import { useTranslations } from "next-intl";
import { toast } from "sonner";

import { captureApiError } from "@/shared/lib/glitchtip";

export function useApiErrorToast() {
  const t = useTranslations();

  return (error: unknown) => {
    if (error instanceof ApiError) {
      const key = errorMessageKey(error.code);
      const message = t.has(key) ? t(key) : error.message;
      toast.error(message);
      captureApiError(error, error.traceId);
      return;
    }
    if (error instanceof Error && error.message.startsWith("auth.")) {
      const key = errorMessageKey(error.message);
      toast.error(t.has(key) ? t(key) : error.message);
      return;
    }
    toast.error(t("errors.common.unknown"));
  };
}
