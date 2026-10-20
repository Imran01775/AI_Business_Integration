"use client";

import { useTranslations } from "next-intl";

import { Link } from "@/i18n/routing";
import { LanguageSwitcher } from "@/shared/ui/language-switcher";

export function PublicHeader() {
  const t = useTranslations("nav");
  const tc = useTranslations("common");
  return (
    <header className="border-b border-border">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4">
        <Link href="/" className="font-semibold">{tc("appName")}</Link>
        <nav className="flex flex-wrap items-center gap-4 text-sm">
          <Link href="/privacy">{t("privacy")}</Link>
          <Link href="/terms">{t("terms")}</Link>
          <Link href="/data-deletion">{t("dataDeletion")}</Link>
          <Link href="/login">{tc("signIn")}</Link>
          <LanguageSwitcher />
        </nav>
      </div>
    </header>
  );
}

export function PublicFooter() {
  const t = useTranslations("nav");
  return (
    <footer className="mt-auto border-t border-border py-8 text-center text-sm text-muted-foreground">
      <div className="flex justify-center gap-4">
        <Link href="/privacy">{t("privacy")}</Link>
        <Link href="/terms">{t("terms")}</Link>
      </div>
    </footer>
  );
}
