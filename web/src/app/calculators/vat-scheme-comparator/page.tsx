import type { Metadata } from "next";
import Link from "next/link";
import { Calculator } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { VATSchemeComparator } from "@/components/calculators/VATSchemeComparator";
import { JsonLd, buildWebApplication } from "@/lib/schema";

export const metadata: Metadata = {
  title: "VAT Scheme Comparator | Standard vs Flat Rate for UK Businesses",
  description:
    "Free VAT scheme comparator for UK businesses. Compares Standard vs Flat Rate (with Limited Cost Trader test) and explains Cash Accounting. ICAEW accountants.",
  alternates: { canonical: `${siteConfig.url}/calculators/vat-scheme-comparator` },
};

export default function VATComparatorPage() {
  const webApp = buildWebApplication({
    name: "VAT Scheme Comparator",
    description:
      "Free UK VAT scheme calculator for limited companies, sole traders and partnerships. Compares Standard VAT against the Flat Rate Scheme using 2025/26 thresholds, including the Limited Cost Trader test.",
    path: "/calculators/vat-scheme-comparator",
    applicationCategory: "FinanceApplication",
  });

  return (
    <>
      <JsonLd data={webApp} />
      <section className="bg-slate-900 py-12 sm:py-16">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Calculators", href: "/calculators" },
              { label: "VAT Scheme Comparator" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free calculator · 2025/26 thresholds
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              VAT Scheme Comparator
            </h1>
            <p className="mt-4 text-lg text-slate-300">
              Compare Standard VAT against the Flat Rate Scheme for your business. Includes the Limited Cost Trader test that catches most service businesses out.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <VATSchemeComparator />

            <div className="mt-12 bg-slate-900 p-8 sm:p-10 text-white">
              <h2 className="text-2xl font-bold text-white sm:text-3xl">VAT setup feeling messy?</h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200">
                We handle VAT registration, scheme selection, MTD compliance and quarterly returns for UK businesses of every shape. Fixed fee, no surprises.
              </p>
              <Link href="/free-health-check" className="mt-6 inline-block bg-orange-600 px-8 py-3 font-bold text-white border-b-4 border-orange-800 hover:bg-orange-700 transition-all">
                Book a free VAT review
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
