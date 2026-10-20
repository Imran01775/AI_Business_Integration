"use client";

import { userSettingsResponseSchema } from "@sales-agent/shared";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { toast } from "sonner";

import { SchemaForm } from "@/shared/ui/schema-form/schema-form";

async function loadSettings() {
  const res = await fetch("/api/bff/api/v1/me/settings");
  if (!res.ok) {
    throw new Error("settings.load_failed");
  }
  const json = await res.json();
  return userSettingsResponseSchema.parse(json);
}

export default function UserSettingsPage() {
  const t = useTranslations("settings");
  const tc = useTranslations("common");
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["me", "settings"], queryFn: loadSettings });

  if (isLoading || !data) {
    return <p>{tc("loading")}</p>;
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>
      <SchemaForm
        schema={data.schema}
        values={data.values}
        saveLabel={tc("save")}
        onSubmit={async (values) => {
          const res = await fetch("/api/bff/api/v1/me/settings", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ values }),
          });
          if (!res.ok) {
            throw new Error("settings.save_failed");
          }
          await queryClient.invalidateQueries({ queryKey: ["me", "settings"] });
          toast.success(t("saved"));
        }}
      />
    </div>
  );
}
