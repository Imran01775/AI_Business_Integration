"use client";

import { useLocale, useTranslations } from "next-intl";

import { locales } from "@sales-agent/i18n";

import { usePathname, useRouter } from "@/i18n/routing";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";

export function LanguageSwitcher() {
  const t = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-muted-foreground">{t("language")}</span>
      <Select
        value={locale}
        onValueChange={(next) => {
          router.replace(pathname, { locale: next as "en" | "bn" });
        }}
      >
        <SelectTrigger className="w-[120px]" aria-label={t("language")}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {locales.map((code) => (
            <SelectItem key={code} value={code}>
              {code === "bn" ? "বাংলা" : "English"}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
