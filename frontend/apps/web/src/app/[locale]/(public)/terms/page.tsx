import { fetchLegalDocument, LegalContent } from "../legal-page";

export default async function TermsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const doc = await fetchLegalDocument("terms", locale);
  return <LegalContent doc={doc} />;
}
