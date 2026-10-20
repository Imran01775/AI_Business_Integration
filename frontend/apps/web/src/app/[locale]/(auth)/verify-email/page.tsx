"use client";

import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Link } from "@/i18n/routing";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

export default function VerifyEmailPage() {
  const t = useTranslations("auth");
  const params = useSearchParams();
  const token = params.get("token");
  const [status, setStatus] = useState<"idle" | "ok" | "error">("idle");

  useEffect(() => {
    if (!token) {
      return;
    }
    void fetch("/api/bff/api/v1/auth/verify-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    }).then((res) => setStatus(res.ok ? "ok" : "error"));
  }, [token]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("verifyEmail")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!token ? <p>{t("verifyInstructions")}</p> : null}
        {token && status === "ok" ? <p>Email verified.</p> : null}
        {token && status === "error" ? <p>Verification failed.</p> : null}
        <Button asChild>
          <Link href="/login">Continue</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
