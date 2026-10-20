import bn from "../messages/bn.json" with { type: "json" };
import en from "../messages/en.json" with { type: "json" };

export const locales = ["en", "bn"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "en";

export const messages: Record<Locale, typeof en> = { en, bn };

/** Resolve API error code to a message key under `errors.*` */
export function errorMessageKey(code: string): string {
  return `errors.${code}`;
}

export function isLocale(value: string): value is Locale {
  return (locales as readonly string[]).includes(value);
}
