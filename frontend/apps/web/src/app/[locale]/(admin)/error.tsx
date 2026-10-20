"use client";

import { useTranslations } from "next-intl";

export default function AdminError() {
  const t = useTranslations("errors");
  return <p>{t("permission.denied")}</p>;
}
