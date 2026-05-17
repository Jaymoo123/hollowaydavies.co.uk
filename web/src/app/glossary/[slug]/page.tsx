import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { BookOpen, ArrowRight } from "lucide-react";
import { siteContainerLg, btnPrimary } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { GLOSSARY } from "./data";
import { JsonLd, buildDefinedTerm } from "@/lib/schema";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return Object.keys(GLOSSARY).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const entry = GLOSSARY[slug];
  if (!entry) return { title: "Term not found" };

  const url = `${siteConfig.url}/glossary/${slug}`;
  return {
    title: `${entry.term}, Definition for UK Business Owners`,
    description: `Plain-English definition of ${entry.term} for UK business owners. Includes current 2025/26 figures and what it means for your business.`,
    alternates: { canonical: url },
    openGraph: {
      title: `${entry.term}, UK Business Tax Glossary`,
      description: `Plain-English definition of ${entry.term} for UK business owners.`,
      url,
      type: "article",
    },
  };
}

export default async function GlossaryEntryPage({ params }: Props) {
  const { slug } = await params;
  const entry = GLOSSARY[slug];
  if (!entry) notFound();

  const related = Object.values(GLOSSARY)
    .filter((e) => e.category === entry.category && e.slug !== entry.slug)
    .slice(0, 3);

  const term = buildDefinedTerm({
    slug,
    term: entry.term,
    definition: entry.body.replace(/<[^>]+>/g, "").slice(0, 250),
    inDefinedTermSet: entry.category,
  });

  return (
    <>
      <JsonLd data={term} />

      <section className="bg-slate-900 py-12 sm:py-16">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Glossary", href: "/glossary" },
              { label: entry.term },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <BookOpen className="h-3.5 w-3.5" />
              {entry.category}
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              {entry.term}
            </h1>
          </div>
        </div>
      </section>

      <article className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-3xl mx-auto">
            <div
              className="article-body prose-blog"
              dangerouslySetInnerHTML={{ __html: entry.body }}
            />

            <div className="mt-12 bg-slate-900 p-8 text-white">
              <h2 className="text-xl font-bold sm:text-2xl">
                Want this applied to your business?
              </h2>
              <p className="mt-3 text-base text-slate-200">
                Book a free call with an ICAEW qualified accountant. We'll review your position and show you what to actually do.
              </p>
              <Link href="/contact" className={`${btnPrimary} mt-6`}>
                Book a free call
              </Link>
            </div>

            {related.length > 0 && (
              <section className="mt-12 pt-12 border-t border-slate-200">
                <h2 className="text-xl font-bold text-slate-900 mb-6">
                  Related terms in {entry.category}
                </h2>
                <ul className="grid gap-3 sm:grid-cols-3">
                  {related.map((r) => (
                    <li key={r.slug}>
                      <Link
                        href={`/glossary/${r.slug}`}
                        className="block bg-slate-50 border border-slate-200 p-4 hover:border-orange-600 hover:bg-white transition-all"
                      >
                        <p className="text-sm font-bold text-slate-900">{r.term}</p>
                      </Link>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </div>
      </article>
    </>
  );
}
