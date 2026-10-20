import { createNavigation } from "next-intl/navigation";
import { defineRouting } from "next-intl/routing";

import { defaultLocale, locales } from "@sales-agent/i18n";

export const routing = defineRouting({
  locales: [...locales],
  defaultLocale,
  localePrefix: "always",
});

export const { Link, redirect, usePathname, useRouter } = createNavigation(routing);
