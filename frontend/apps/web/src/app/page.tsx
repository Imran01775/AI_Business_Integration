import { redirect } from "next/navigation";

import { defaultLocale } from "@sales-agent/i18n";

export default function RootPage() {
  redirect(`/${defaultLocale}`);
}
