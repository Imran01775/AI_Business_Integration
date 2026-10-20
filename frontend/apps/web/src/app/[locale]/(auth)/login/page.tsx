"use client";

import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { useLogin } from "@/features/auth";
import { Link, useRouter } from "@/i18n/routing";
import { useApiErrorToast } from "@/shared/lib/api-error-toast";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

export default function LoginPage() {
  const t = useTranslations("auth");
  const tc = useTranslations("common");
  const router = useRouter();
  const params = useSearchParams();
  const toastError = useApiErrorToast();
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <Card>
      <CardHeader>
        <CardTitle>{tc("signIn")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">{t("email")}</Label>
          <Input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">{t("password")}</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <Button
          className="w-full"
          disabled={login.isPending}
          onClick={() => {
            login.mutate(
              { email, password },
              {
                onSuccess: () => {
                  const next = params.get("next") ?? "/seller";
                  router.push(next);
                },
                onError: toastError,
              },
            );
          }}
        >
          {tc("signIn")}
        </Button>
        <p className="text-center text-sm">
          {t("noAccount")}{" "}
          <Link href="/register" className="underline">
            {tc("register")}
          </Link>
        </p>
        <p className="text-center text-sm">
          <Link href="/forgot-password" className="underline">{t("forgotPassword")}</Link>
        </p>
      </CardContent>
    </Card>
  );
}
