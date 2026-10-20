"use client";

import { useTranslations } from "next-intl";

import { Button } from "@/shared/ui/button";

export default function PublicError({ reset }: { reset: () => void }) {
  const t = useTranslations("errors");
  return (
    <div className="space-y-4 text-center">
      <h2 className="text-xl font-semibold">{t("common.unknown")}</h2>
      <Button onClick={reset}>Retry</Button>
    </div>
  );
}
