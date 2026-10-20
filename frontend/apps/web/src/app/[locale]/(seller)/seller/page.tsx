"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

import { useLogout } from "@/features/auth";
import { useRouter } from "@/i18n/routing";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

export default function SellerDashboardPage() {
  const t = useTranslations("tenant");
  const tc = useTranslations("common");
  const router = useRouter();
  const logout = useLogout();
  const [displayName, setDisplayName] = useState("");
  const [slug, setSlug] = useState("");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{tc("appName")}</h1>
        <Button
          variant="outline"
          onClick={() => {
            logout.mutate(undefined, { onSuccess: () => router.push("/login") });
          }}
        >
          {tc("signOut")}
        </Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{t("create")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <Label>{t("name")}</Label>
            <Input value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>{t("slug")}</Label>
            <Input value={slug} onChange={(e) => setSlug(e.target.value)} />
          </div>
          <Button
            onClick={() => {
              void fetch("/api/bff/api/v1/tenants", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  display_name: displayName,
                  slug,
                  timezone: "Asia/Dhaka",
                  locale: "en",
                  currency: "BDT",
                }),
              }).then(() => router.refresh());
            }}
          >
            {t("create")}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
