import type { Metadata } from "next";
import Link from "next/link";
import { Calculator, ArrowRight } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: `Free UK Tax Calculators for Business Owners | ${siteConfig.name}`,
  description:
    "Free tax and finance calculators for UK limited companies, contractors, sole traders and small businesses. Salary vs dividend optimiser using 2025/26 rates. Built by ICAEW qualified accountants.",
  alternates: { canonical: `${siteConfig.url}/calculators` },
  openGraph: {
    title: "Free UK Tax Calculators for Business Owners",
    description: "Free tax and finance calculators for UK businesses. Salary vs dividend, take-home and more.",
    url: `${siteConfig.url}/calculators`,
    type: "website",
  },
};

const calculators = [
  {
    slug: "salary-dividend-optimiser",
    title: "Salary & Dividend Optimiser",
    description:
      "Stop guessing the split. Drop your profit in and see exactly how much salary versus dividend leaves the most cash in your pocket at 2025/26 rates.",
    available: true,
  },
  {
    slug: "rd-tax-credit-estimator",
    title: "R&D Tax Credit Estimator",
    description:
      "Plug in your qualifying spend and see your indicative claim under the merged scheme, plus what the R&D-intensive enhanced rate would unlock if you qualify.",
    available: true,
  },
  {
    slug: "badr-cgt-calculator",
    title: "BADR CGT Calculator",
    description:
      "See your post-relief CGT on a business sale, your remaining lifetime allowance, and what the 6 April 2026 rate jump from 14% to 18% costs if you slip into the next tax year.",
    available: true,
  },
  {
    slug: "vat-scheme-comparator",
    title: "VAT Scheme Comparator",
    description:
      "Most service businesses leave money on the table picking VAT schemes by instinct. Run your numbers and find out whether Flat Rate beats Standard, and whether Limited Cost Trader forces you to 16.5%.",
    available: true,
  },
  {
    slug: "pension-contribution-optimiser",
    title: "Pension Contribution Optimiser",
    description:
      "For owner-managed Ltds, pension is usually the cheapest way out of retained profit. See the corporation tax saved, the net cost, and the headroom against the £60,000 annual allowance taper.",
    available: true,
  },
  {
    slug: "take-home-pay-calculator",
    title: "Take-Home Pay Calculator",
    description:
      "Gross salary in, annual, monthly and weekly net out. Handles 2025/26 income tax bands, employee NI, all four student loan plans and salary-sacrifice pension contributions in one go.",
    available: true,
  },
  {
    slug: "employer-ni-calculator",
    title: "Employer NI & Cost-to-Hire",
    description:
      "Hiring is never as cheap as the offer letter. See the full annual cost across your payroll with employer NI at 15%, the Employment Allowance offset, and the 3% pension contribution on qualifying earnings.",
    available: true,
  },
];

export default function CalculatorsIndexPage() {
  return (
    <>
      <section className="bg-slate-900 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Calculators" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free tools
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Free UK tax calculators for business owners
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              We built these to answer the questions UK business owners actually ask us: what is my real take-home pay, how much salary versus dividend, what does an extra hire cost, and how much CGT will I pay on the exit. All numbers reflect 2025/26 rates and thresholds. No email gate, no sign-up.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto grid gap-6 sm:gap-8 md:grid-cols-2 lg:grid-cols-3">
            {calculators.map((c) => (
              <Link
                key={c.slug}
                href={`/calculators/${c.slug}`}
                className="group block bg-slate-50 border border-slate-200 p-6 sm:p-8 hover:bg-white hover:border-orange-600 hover:shadow-md transition-all"
              >
                <div className="flex items-center justify-center h-12 w-12 bg-gradient-to-br from-orange-500 to-orange-700 shadow-sm">
                  <Calculator className="h-6 w-6 text-white" />
                </div>
                <h2 className="mt-5 text-xl font-bold text-slate-900 group-hover:text-orange-700 transition-colors">
                  {c.title}
                </h2>
                <p className="mt-3 text-sm text-slate-600 leading-relaxed">{c.description}</p>
                <div className="mt-5 flex items-center text-orange-600 font-semibold text-sm">
                  Open calculator
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
