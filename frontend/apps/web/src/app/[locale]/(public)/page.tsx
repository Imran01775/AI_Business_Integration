import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/routing";
import { Button } from "@/shared/ui/button";

export default async function HomePage() {
  const t = await getTranslations("common");
  const nav = await getTranslations("nav");
  return (
    <section className="space-y-6">
      <h1 className="text-4xl font-bold tracking-tight">{t("appName")}</h1>
      <p className="max-w-2xl text-lg text-muted-foreground">
        Messenger-native AI sales assistant for Bangladeshi businesses — catalogue, orders, and human handoff in one panel.
      </p>
      <div className="flex gap-3">
        <Button asChild>
          <Link href="/register">{t("register")}</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/login">{t("signIn")}</Link>
        </Button>
        <Button variant="ghost" asChild>
          <Link href="/privacy">{nav("privacy")}</Link>
        </Button>
      </div>
    </section>
  );
}
