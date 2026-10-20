import { notFound } from "next/navigation";

import { getBackendUrl } from "@/shared/config/env";

type LegalDoc = {
  body_html: string;
  version: number;
  updated_at: string;
};

export async function fetchLegalDocument(document: string, locale: string): Promise<LegalDoc> {
  const base = getBackendUrl();
  const res = await fetch(`${base}/api/v1/public/legal/${document}?locale=${locale}`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) {
    notFound();
  }
  return (await res.json()) as LegalDoc;
}

export function LegalContent({ doc }: { doc: LegalDoc }) {
  return (
    <article className="prose prose-neutral max-w-none dark:prose-invert">
      <p className="text-xs text-muted-foreground">
        v{doc.version} · {new Date(doc.updated_at).toLocaleDateString()}
      </p>
      <div dangerouslySetInnerHTML={{ __html: doc.body_html }} />
    </article>
  );
}
