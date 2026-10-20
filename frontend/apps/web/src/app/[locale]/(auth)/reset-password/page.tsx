"use client";

import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { Link } from "@/i18n/routing";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

export default function ResetPasswordPage() {
  const t = useTranslations("auth");
  const params = useSearchParams();
  const token = params.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [done, setDone] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("resetPassword")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {done ? (
          <Button asChild>
            <Link href="/login">Sign in</Link>
          </Button>
        ) : (
          <>
            <div className="space-y-2">
              <Label htmlFor="password">{t("password")}</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <Button
              className="w-full"
              onClick={() => {
                void fetch("/api/bff/api/v1/auth/password-reset/confirm", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ token, new_password: password }),
                }).then((res) => {
                  if (res.ok) {
                    setDone(true);
                  }
                });
              }}
            >
              {t("resetPassword")}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
