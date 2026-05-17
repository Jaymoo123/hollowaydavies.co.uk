import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { CheckCircle2, FileText } from "lucide-react";
import { siteContainerLg, btnPrimary } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { PrintButton } from "@/components/ui/PrintButton";
import { GUIDES } from "../data";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return Object.keys(GUIDES).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const guide = GUIDES[slug];
  if (!guide) return { title: "Guide not found" };
  // Don't index download pages, they should rank as the landing version
  return {
    title: `${guide.title} | Download`,
    description: guide.teaser,
    robots: { index: false, follow: true },
  };
}

export default async function GuideDownloadPage({ params }: Props) {
  const { slug } = await params;
  const guide = GUIDES[slug];
  if (!guide) notFound();

  return (
    <>
      <section className="bg-slate-900 py-12">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Guides", href: "/guides" },
              { label: guide.title, href: `/guides/${guide.slug}` },
              { label: "Download" },
            ]}
          />
          <div className="mt-6 max-w-4xl">
            <div className="inline-flex items-center gap-2 bg-emerald-500 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Guide unlocked
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl leading-tight">
              {guide.title}
            </h1>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center justify-between gap-4 bg-orange-50 border border-orange-200 p-4 mb-8 print:hidden">
              <div className="flex items-center gap-3">
                <FileText className="h-6 w-6 text-orange-600 flex-shrink-0" />
                <p className="text-sm text-orange-900">
                  <strong>Tip:</strong> hit print and save as PDF for offline use.
                </p>
              </div>
              <PrintButton />
            </div>

            <div className="article-body prose-blog" dangerouslySetInnerHTML={{ __html: guide.body }} />

            <div className="mt-12 bg-slate-900 p-8 sm:p-10 text-white print:hidden">
              <h2 className="text-2xl font-bold sm:text-3xl">Want this applied to your business?</h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200">
                Book a free call with an ICAEW qualified accountant. We'll review your specific situation and tell you exactly what to do.
              </p>
              <Link href="/contact" className={`${btnPrimary} mt-6`}>
                Book a free call
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
