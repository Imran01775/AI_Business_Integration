"use client";

import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";

import { useRegister } from "@/features/auth";
import { Link, useRouter } from "@/i18n/routing";
import { useApiErrorToast } from "@/shared/lib/api-error-toast";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

export default function RegisterPage() {
  const t = useTranslations("auth");
  const tc = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();
  const register = useRegister();
  const toastError = useApiErrorToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");

  return (
    <Card>
      <CardHeader>
        <CardTitle>{tc("register")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="displayName">{t("displayName")}</Label>
          <Input id="displayName" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">{t("email")}</Label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">{t("password")}</Label>
          <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <Button
          className="w-full"
          disabled={register.isPending}
          onClick={() => {
            register.mutate(
              { email, password, display_name: displayName, locale },
              {
                onSuccess: () => router.push("/verify-email"),
                onError: toastError,
              },
            );
          }}
        >
          {tc("register")}
        </Button>
        <p className="text-center text-sm">
          {t("hasAccount")}{" "}
          <Link href="/login" className="underline">
            {tc("signIn")}
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
