import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Download, BadgeCheck, FileText } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { LeadForm } from "@/components/forms/LeadForm";
import { GUIDES } from "./data";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return Object.keys(GUIDES).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const guide = GUIDES[slug];
  if (!guide) return { title: "Guide not found" };

  const url = `${siteConfig.url}/guides/${slug}`;
  return {
    title: `${guide.title} | Free Guide`,
    description: guide.teaser,
    alternates: { canonical: url },
    openGraph: { title: guide.title, description: guide.teaser, url, type: "article" },
  };
}

export default async function GuideLandingPage({ params }: Props) {
  const { slug } = await params;
  const guide = GUIDES[slug];
  if (!guide) notFound();

  return (
    <>
      <section className="bg-slate-900 py-12 sm:py-16">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Guides", href: "/guides" },
              { label: guide.title },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <FileText className="h-3.5 w-3.5" />
              {guide.category}
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl leading-tight">
              {guide.title}
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">{guide.teaser}</p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto grid gap-8 lg:grid-cols-[1fr_400px]">
            <div>
              <h2 className="text-xl font-bold text-slate-900 mb-4">What's inside</h2>
              <ul className="space-y-3 text-base text-slate-700">
                {[
                  "Specific actionable steps with deadlines",
                  "2025/26 UK tax figures throughout",
                  "Real software, HMRC form references, and worked examples",
                  "Written by ICAEW qualified accountants",
                  "Free, no obligation, no follow-up sales calls",
                ].map((b) => (
                  <li key={b} className="flex items-start gap-3">
                    <BadgeCheck className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>

              <div className="mt-8 bg-slate-50 border-l-4 border-orange-600 p-6">
                <h3 className="text-base font-bold text-slate-900">Why we publish these for free</h3>
                <p className="mt-2 text-sm text-slate-700 leading-relaxed">
                  We work with UK business owners across every sector: limited companies, contractors, sole traders, partnerships and growing SMEs. The patterns we see repeat. Publishing the playbooks publicly is how we demonstrate the value of working with us. If you find this useful and want it applied to your specific situation, a free call is where that conversation starts.
                </p>
              </div>
            </div>

            <aside>
              <div className="bg-orange-50 border-2 border-orange-600 p-6 sm:p-8 sticky top-24">
                <div className="flex items-center justify-center h-14 w-14 bg-orange-600 mb-4">
                  <Download className="h-7 w-7 text-white" />
                </div>
                <h2 className="text-xl font-bold text-orange-900">Get the full guide</h2>
                <p className="mt-2 text-sm text-slate-700">
                  Drop your email and we'll send you the full guide right away. No spam, no follow-up calls unless you ask.
                </p>
                <div className="mt-5">
                  <LeadForm
                    successRedirect={`/guides/${guide.slug}/download`}
                    submitLabel="Get the guide"
                  />
                </div>
                <p className="mt-4 text-xs text-slate-500">
                  By submitting you agree to receive this guide and occasional related insights. Unsubscribe any time.
                </p>
              </div>
            </aside>
          </div>
        </div>
      </section>
    </>
  );
}
