"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";

type Workspace = { id: string; slug: string; display_name: string; role: string };

async function fetchWorkspaces(): Promise<Workspace[]> {
  const res = await fetch("/api/bff/api/v1/me/workspaces");
  if (!res.ok) {
    return [];
  }
  const data = (await res.json()) as { data: Workspace[] };
  return data.data;
}

export function TenantSwitcher() {
  const t = useTranslations("tenant");
  const { data = [] } = useQuery({ queryKey: ["workspaces"], queryFn: fetchWorkspaces });
  const [tenantId, setTenantId] = useState<string | undefined>();

  useEffect(() => {
    const stored = window.localStorage.getItem("tenant_id");
    if (stored) {
      setTenantId(stored);
    } else if (data[0]) {
      setTenantId(data[0].id);
      window.localStorage.setItem("tenant_id", data[0].id);
      document.cookie = `tenant_id=${data[0].id}; path=/; SameSite=Lax`;
    }
  }, [data]);

  if (data.length === 0) {
    return null;
  }

  return (
    <div className="px-2 py-2">
      <p className="mb-2 text-xs text-muted-foreground">{t("switch")}</p>
      <Select
        value={tenantId}
        onValueChange={(id) => {
          setTenantId(id);
          window.localStorage.setItem("tenant_id", id);
          document.cookie = `tenant_id=${id}; path=/; SameSite=Lax`;
        }}
      >
        <SelectTrigger aria-label={t("switch")}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {data.map((w) => (
            <SelectItem key={w.id} value={w.id}>
              {w.display_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
