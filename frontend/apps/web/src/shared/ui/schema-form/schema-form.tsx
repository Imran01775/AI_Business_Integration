"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { SettingFieldSchema } from "@sales-agent/shared";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";
import { Switch } from "@/shared/ui/switch";

export type SchemaFormProps = {
  schema: Record<string, SettingFieldSchema>;
  values: Record<string, unknown>;
  disabledKeys?: Set<string>;
  saveLabel: string;
  onSubmit: (values: Record<string, unknown>) => Promise<void>;
};

function fieldLabel(key: string, field: SettingFieldSchema): string {
  return field.title ?? key;
}

export function SchemaForm({ schema, values, disabledKeys, saveLabel, onSubmit }: SchemaFormProps) {
  const form = useForm<Record<string, unknown>>({ defaultValues: values });

  useEffect(() => {
    form.reset(values);
  }, [form, values]);

  return (
    <form
      className="space-y-6"
      onSubmit={form.handleSubmit(async (data) => {
        await onSubmit(data);
      })}
    >
      {Object.entries(schema).map(([key, field]) => {
        const disabled = disabledKeys?.has(key) ?? field.readOnly === true;
        const id = `field-${key}`;
        if (field.type === "bool") {
          return (
            <div key={key} className="flex items-center justify-between gap-4">
              <div>
                <Label htmlFor={id}>{fieldLabel(key, field)}</Label>
                {field.description ? <p className="text-sm text-muted-foreground">{field.description}</p> : null}
              </div>
              <Switch
                id={id}
                disabled={disabled}
                checked={Boolean(form.watch(key))}
                onCheckedChange={(checked) => form.setValue(key, checked)}
              />
            </div>
          );
        }
        if (field.enum && field.enum.length > 0) {
          return (
            <div key={key} className="space-y-2">
              <Label htmlFor={id}>{fieldLabel(key, field)}</Label>
              <Select
                disabled={disabled}
                value={String(form.watch(key) ?? "")}
                onValueChange={(v) => form.setValue(key, v)}
              >
                <SelectTrigger id={id}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {field.enum.map((option) => (
                    <SelectItem key={String(option)} value={String(option)}>
                      {String(option)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          );
        }
        return (
          <div key={key} className="space-y-2">
            <Label htmlFor={id}>{fieldLabel(key, field)}</Label>
            <Input
              id={id}
              disabled={disabled}
              value={String(form.watch(key) ?? "")}
              onChange={(e) => form.setValue(key, e.target.value)}
            />
          </div>
        );
      })}
      <Button type="submit">{saveLabel}</Button>
    </form>
  );
}
