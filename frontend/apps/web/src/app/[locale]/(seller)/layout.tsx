import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/routing";
import { LanguageSwitcher } from "@/shared/ui/language-switcher";
import { TenantSwitcher } from "@/shared/ui/tenant-switcher";

export default async function SellerLayout({ children }: { children: React.ReactNode }) {
  const t = await getTranslations("nav");
  const tc = await getTranslations("common");
  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-64 border-r border-border bg-muted/20 p-4 md:block">
        <p className="mb-4 font-semibold">{tc("appName")}</p>
        <TenantSwitcher />
        <nav className="mt-6 flex flex-col gap-2 text-sm">
          <Link href="/seller">{t("dashboard")}</Link>
          <Link href="/settings/me">{t("settings")}</Link>
        </nav>
        <div className="mt-8">
          <LanguageSwitcher />
        </div>
      </aside>
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border px-4 py-3 md:hidden">
          <span className="font-medium">{t("dashboard")}</span>
          <LanguageSwitcher />
        </header>
        <main className="flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
