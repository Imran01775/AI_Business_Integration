"use client";

import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";

import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

export default function ForgotPasswordPage() {
  const t = useTranslations("auth");
  const locale = useLocale();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("forgotPassword")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sent ? (
          <p>Check your email for reset instructions.</p>
        ) : (
          <>
            <div className="space-y-2">
              <Label htmlFor="email">{t("email")}</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <Button
              className="w-full"
              onClick={() => {
                void fetch("/api/bff/api/v1/auth/password-reset/request", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ email, locale }),
                }).then(() => setSent(true));
              }}
            >
              Send reset link
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
