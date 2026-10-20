import { fetchLegalDocument, LegalContent } from "../legal-page";

export default async function DataDeletionPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const doc = await fetchLegalDocument("data-deletion", locale);
  return <LegalContent doc={doc} />;
}
