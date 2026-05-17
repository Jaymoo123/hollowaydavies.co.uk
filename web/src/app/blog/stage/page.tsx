import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { Breadcrumb } from "@/components/ui/Breadcrumb";

export const metadata: Metadata = {
  title: `Insights by business stage | ${siteConfig.name}`,
  description:
    "UK tax, structure and finance articles grouped by where you are in the business lifecycle: starting, running, scaling or exiting.",
  alternates: { canonical: `${siteConfig.url}/blog/stage` },
};

const STAGES = [
  {
    slug: "starting-a-business",
    name: "Starting a business",
    summary:
      "Sole trader vs limited company, incorporation, first VAT registration, registering for self-assessment, first 90 days.",
    keywords: "Set up. Register. First step.",
  },
  {
    slug: "running-a-business",
    name: "Running a business",
    summary:
      "Bookkeeping, payroll, VAT returns, corporation tax, dividends, director pay. The operational tax decisions month-to-month.",
    keywords: "Day-to-day. Monthly. Quarterly. Yearly.",
  },
  {
    slug: "scaling-a-business",
    name: "Scaling a business",
    summary:
      "Hiring, R&D claims, holding companies, restructuring, alphabet shares, associated company rules. Tax for growth.",
    keywords: "Hire. Restructure. Optimise.",
  },
  {
    slug: "exiting-a-business",
    name: "Exiting a business",
    summary:
      "BADR planning, MVL vs strike-off, earn-out structures, due diligence prep. The 12-24 months before exit are where the tax saving happens.",
    keywords: "Sell. Wind down. Hand over.",
  },
];

export default function BlogStageIndexPage() {
  return (
    <>
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <Breadcrumb
            items={[
              { label: "Home", href: "/" },
              { label: "Insights", href: "/blog" },
              { label: "By stage" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              Browse by stage
            </p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl lg:text-6xl">
              Where are you?
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-neutral-600 max-w-2xl">
              Tax and structure decisions look different at every stage. Pick the one closest to where your business is now.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto grid gap-6 sm:grid-cols-2">
            {STAGES.map((s) => (
              <Link
                key={s.slug}
                href={`/blog/stage/${s.slug}`}
                className="group flex h-full flex-col border border-neutral-200 bg-white p-7 transition-all hover:border-orange-600 hover:shadow-md"
              >
                <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                  {s.keywords}
                </p>
                <h2 className="mt-3 text-2xl font-bold text-neutral-900">
                  {s.name}
                </h2>
                <p className="mt-3 flex-grow text-base text-neutral-600 leading-relaxed">
                  {s.summary}
                </p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-orange-700 group-hover:text-orange-800">
                  Browse articles
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
