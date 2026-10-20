import { PublicFooter, PublicHeader } from "@/shared/ui/public-shell";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <PublicHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">{children}</main>
      <PublicFooter />
    </div>
  );
}
