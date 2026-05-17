import type { Metadata } from "next";
import Link from "next/link";
import { Download, FileText } from "lucide-react";
import { siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { SignupForm } from "@/components/newsletter/SignupForm";

export const metadata: Metadata = {
  title: `Free UK Business Templates | ${siteConfig.name}`,
  description:
    "Free downloadable PDF templates for UK limited companies, sole traders and contractors. Invoice template, year-end checklist, MTD ITSA checklist, mileage log, dividend voucher, board minutes, monthly expense tracker. ICAEW reviewed.",
  alternates: { canonical: `${siteConfig.url}/templates` },
  openGraph: {
    title: `Free UK Business Templates | ${siteConfig.name}`,
    description: "Free PDF templates: invoice, expense tracker, year-end checklist, MTD ITSA checklist and more.",
    url: `${siteConfig.url}/templates`,
    type: "website",
  },
};

const TEMPLATES = [
  {
    slug: "invoice-template",
    title: "UK invoice template",
    summary: "VAT-aware invoice template for UK businesses. Compatible with sole traders, limited companies and partnerships. Replace the bracketed placeholders.",
    audience: "Every UK business issuing invoices",
  },
  {
    slug: "expense-tracker",
    title: "Monthly expense tracker",
    summary: "One-page monthly expense log with HMRC-aligned categories. Use to reconcile bank statements before posting to your bookkeeping software.",
    audience: "Sole traders, freelancers, small Ltd companies",
  },
  {
    slug: "year-end-checklist",
    title: "Limited company year-end tax checklist",
    summary: "23-item checklist for the 4-6 weeks before your company year-end. Covers salary review, dividend timing, AIA, R&D claim prep and post-year-end filings.",
    audience: "Limited company directors",
  },
  {
    slug: "mtd-itsa-checklist",
    title: "MTD for Income Tax quarterly checklist",
    summary: "Pre-MTD setup steps + per-quarter and end-of-period workflow. For self-employed and landlords with qualifying income over £50,000 from April 2026.",
    audience: "Sole traders and landlords",
  },
  {
    slug: "mileage-log",
    title: "Business mileage log",
    summary: "HMRC-compliant mileage log using AMAP rates (45p first 10,000 miles, 25p thereafter). Track 22 trips per page, auto-calculates the claim.",
    audience: "Anyone driving a personal vehicle for business",
  },
  {
    slug: "dividend-voucher",
    title: "Dividend voucher template",
    summary: "Companies Act 2006 compliant dividend voucher. Required by law for every dividend payment. Keep with company records for at least 6 years.",
    audience: "Limited company directors paying dividends",
  },
  {
    slug: "board-minutes",
    title: "Board minutes (interim dividend declaration)",
    summary: "Template for single-director or multi-director Ltd companies. Minutes the dividend declaration and confirms distributable reserves were checked.",
    audience: "Limited company directors",
  },
];

export default function TemplatesIndexPage() {
  return (
    <>
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <Breadcrumb
            items={[
              { label: "Home", href: "/" },
              { label: "Templates" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              Free templates
            </p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl lg:text-6xl">
              UK business templates, free.
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-neutral-600 max-w-2xl">
              Seven PDF templates for UK limited companies, contractors and sole traders. Each one reviewed by an ICAEW Chartered Accountant. Download, fill in, use. No email required.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto grid gap-6 sm:gap-8 md:grid-cols-2 lg:grid-cols-3">
            {TEMPLATES.map((t) => (
              <article
                key={t.slug}
                className="group flex h-full flex-col border border-neutral-200 bg-white p-6 sm:p-7 transition-all hover:border-orange-600 hover:shadow-md"
              >
                <div className="flex items-center justify-center h-12 w-12 bg-gradient-to-br from-orange-500 to-orange-700 shadow-sm">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <h2 className="mt-5 text-xl font-bold text-neutral-900">
                  {t.title}
                </h2>
                <p className="mt-2 text-xs font-mono uppercase tracking-wider text-neutral-500">
                  {t.audience}
                </p>
                <p className="mt-3 flex-grow text-sm text-neutral-600 leading-relaxed">
                  {t.summary}
                </p>
                <a
                  href={`/templates/${t.slug}.pdf`}
                  download
                  className="mt-5 inline-flex items-center justify-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-4 py-2.5 text-sm font-bold transition-colors"
                >
                  <Download className="h-4 w-4" />
                  Download PDF
                </a>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#fafaf7] py-16 border-t border-neutral-200">
        <div className={siteContainerLg}>
          <div className="max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-neutral-900 sm:text-3xl">
              About the templates
            </h2>
            <p className="mt-4 text-base text-neutral-700 leading-relaxed">
              Every template is reviewed by James Holloway, ICAEW Chartered Accountant, against current HMRC and Companies House requirements. They are not a substitute for tailored tax advice, but they cover the standard documents most UK limited companies, contractors, sole traders and small businesses need.
            </p>
            <p className="mt-4 text-base text-neutral-700 leading-relaxed">
              No email required. Share them freely with your team, your accountant, or your network. If something is wrong or out of date, get in touch and the editorial team will fix it.
            </p>
            <div className="mt-10 max-w-xl">
              <SignupForm
                source="templates"
                variant="card"
                heading="Want new templates as we publish them?"
                body="Subscribe to The Director&rsquo;s Brief and we&rsquo;ll send you new templates when they land, plus one short tax-and-finance email a week."
                ctaLabel="Subscribe"
              />
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
