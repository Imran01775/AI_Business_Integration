import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/routing";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const t = await getTranslations("nav");
  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-6">
          <span className="font-semibold">{t("admin")}</span>
          <Link href="/admin">Overview</Link>
        </div>
      </header>
      <main className="p-6">{children}</main>
    </div>
  );
}
