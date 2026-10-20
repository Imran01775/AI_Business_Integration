import { fetchLegalDocument, LegalContent } from "../legal-page";

export default async function PrivacyPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const doc = await fetchLegalDocument("privacy", locale);
  return <LegalContent doc={doc} />;
}
