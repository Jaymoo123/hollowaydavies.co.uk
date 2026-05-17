import type { Metadata } from "next";
import Link from "next/link";
import { FileText, ArrowRight, Download } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { GUIDES } from "./[slug]/data";

export const metadata: Metadata = {
  title: `Free Guides | ${siteConfig.name}`,
  description:
    "Free in-depth guides for UK business owners. Year-end tax checklist, switching accountants playbook, first 90 days post-incorporation, contractor playbook.",
  alternates: { canonical: `${siteConfig.url}/guides` },
};

export default function GuidesIndexPage() {
  const guides = Object.values(GUIDES);
  return (
    <>
      <section className="bg-slate-900 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Free Guides" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <FileText className="h-3.5 w-3.5" />
              Free downloadable guides
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Free in-depth guides
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              Long-form practical guides for UK business owners. Year-end tax planning, switching accountants, first 90 days as a Ltd company, contractor first contract. Drop your email to get the full version.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto grid gap-6 sm:gap-8 md:grid-cols-2">
            {guides.map((g) => (
              <Link
                key={g.slug}
                href={`/guides/${g.slug}`}
                className="group block bg-slate-50 border border-slate-200 p-6 sm:p-8 hover:bg-white hover:border-orange-600 hover:shadow-md transition-all"
              >
                <div className="flex items-center justify-center h-12 w-12 bg-gradient-to-br from-orange-500 to-orange-700 shadow-sm">
                  <Download className="h-6 w-6 text-white" />
                </div>
                <p className="mt-5 text-xs font-bold uppercase tracking-wider text-orange-700">
                  {g.category}
                </p>
                <h2 className="mt-2 text-xl font-bold text-slate-900 group-hover:text-orange-700 transition-colors leading-snug">
                  {g.title}
                </h2>
                <p className="mt-3 text-sm text-slate-600 leading-relaxed">{g.teaser}</p>
                <div className="mt-5 flex items-center text-orange-600 font-semibold text-sm">
                  Get the guide
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
