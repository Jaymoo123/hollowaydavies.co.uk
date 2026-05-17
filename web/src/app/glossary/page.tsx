import type { Metadata } from "next";
import Link from "next/link";
import { BookOpen, ArrowRight } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { GLOSSARY } from "./[slug]/data";

export const metadata: Metadata = {
  title: `Glossary | ${siteConfig.name}`,
  description:
    "Plain-English definitions of UK tax, finance, and accounting terms for business owners. BADR, IR35, MTD, R&D credits, VAT schemes and more.",
  alternates: { canonical: `${siteConfig.url}/glossary` },
  openGraph: {
    title: "Glossary | UK Business Tax & Finance Terms Explained",
    description: "Plain-English definitions for UK business owners.",
    url: `${siteConfig.url}/glossary`,
    type: "website",
  },
};

export default function GlossaryIndexPage() {
  const entries = Object.values(GLOSSARY);

  // Group by category
  const byCategory: Record<string, typeof entries> = {};
  for (const e of entries) {
    (byCategory[e.category] ||= []).push(e);
  }
  const categories = Object.keys(byCategory).sort();

  return (
    <>
      <section className="bg-slate-900 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Glossary" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <BookOpen className="h-3.5 w-3.5" />
              Plain English definitions
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              UK business tax &amp; finance glossary
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              {entries.length} definitions of the terms UK business owners actually need to understand. Written by ICAEW qualified accountants. All figures verified for 2025/26.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto">
            {categories.map((cat) => (
              <div key={cat} className="mb-12 last:mb-0">
                <h2 className="text-2xl font-bold text-slate-900 mb-6 pb-3 border-b border-slate-200">
                  {cat}
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {byCategory[cat].map((e) => (
                    <Link
                      key={e.slug}
                      href={`/glossary/${e.slug}`}
                      className="group block bg-slate-50 border border-slate-200 p-5 hover:bg-white hover:border-orange-600 hover:shadow-md transition-all"
                    >
                      <h3 className="text-lg font-bold text-slate-900 group-hover:text-orange-700 transition-colors">
                        {e.term}
                      </h3>
                      <div className="mt-3 flex items-center text-orange-600 font-semibold text-sm">
                        Read definition
                        <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
