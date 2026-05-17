import type { Metadata } from "next";
import Link from "next/link";
import { Calculator } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { BADRCalculator } from "@/components/calculators/BADRCalculator";
import { JsonLd, buildWebApplication } from "@/lib/schema";

export const metadata: Metadata = {
  title: "BADR Calculator 2025/26 | UK Business Sale CGT",
  description:
    "Free BADR (Business Asset Disposal Relief) calculator. Models 2025/26 14% rate and 2026/27 18% rate, lifetime £1M limit, eligibility tests. ICAEW accountants.",
  alternates: { canonical: `${siteConfig.url}/calculators/badr-cgt-calculator` },
};

export default function BADRPage() {
  const webApp = buildWebApplication({
    name: "BADR Calculator 2025/26",
    description:
      "Free UK Business Asset Disposal Relief calculator. Models 14% rate (2025/26), 18% rate from 6 April 2026, £1M lifetime limit, and the 2-year qualifying period.",
    path: "/calculators/badr-cgt-calculator",
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
              { label: "BADR Calculator" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free calculator · 14% rate 2025/26 · 18% rate 2026/27
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              BADR Calculator
            </h1>
            <p className="mt-4 text-lg text-slate-300">
              Work out your CGT bill on a business sale under Business Asset Disposal Relief. Models the £1M lifetime limit, the rate increase from 6 April 2026, and the eligibility tests.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <BADRCalculator />

            <div className="mt-12 bg-slate-900 p-8 sm:p-10 text-white">
              <h2 className="text-2xl font-bold text-white sm:text-3xl">Selling before 6 April 2026?</h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200">
                The BADR rate rises from 14% to 18% on 6 April 2026. If you're planning a sale in the next 18 months, timing matters. We help business owners plan exits to capture the lower rate.
              </p>
              <Link href="/free-health-check" className="mt-6 inline-block bg-orange-600 px-8 py-3 font-bold text-white border-b-4 border-orange-800 hover:bg-orange-700 transition-all">
                Book an exit-timing call
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
