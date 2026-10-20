import { getTranslations } from "next-intl/server";

export default async function AdminPage() {
  const t = await getTranslations("nav");
  return (
    <div>
      <h1 className="text-2xl font-semibold">{t("admin")}</h1>
      <p className="mt-2 text-muted-foreground">Platform console (Phase 05+).</p>
    </div>
  );
}
