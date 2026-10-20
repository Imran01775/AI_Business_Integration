import { z } from "zod";

export const settingFieldSchema = z.object({
  type: z.string(),
  default: z.unknown().optional(),
  title: z.string().optional(),
  description: z.string().optional(),
  enum: z.array(z.union([z.string(), z.number(), z.boolean()])).optional(),
  format: z.string().optional(),
  readOnly: z.boolean().optional(),
});

export type SettingFieldSchema = z.infer<typeof settingFieldSchema>;

export const userSettingsResponseSchema = z.object({
  schema: z.record(settingFieldSchema),
  values: z.record(z.unknown()),
});

export type UserSettingsResponse = z.infer<typeof userSettingsResponseSchema>;
