import type { Metadata } from "next";
import Link from "next/link";
import { Calculator } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { RDCreditEstimator } from "@/components/calculators/RDCreditEstimator";
import { JsonLd, buildWebApplication } from "@/lib/schema";

export const metadata: Metadata = {
  title: "R&D Tax Credit Estimator 2025/26 | UK Business Calculator",
  description:
    "Free R&D tax credit estimator for UK businesses. Models the post-April 2023 merged scheme + R&D intensive enhanced rate. Built by ICAEW accountants.",
  alternates: { canonical: `${siteConfig.url}/calculators/rd-tax-credit-estimator` },
};

export default function RDCreditPage() {
  const webApp = buildWebApplication({
    name: "R&D Tax Credit Estimator 2025/26",
    description:
      "Free UK R&D tax credit estimator for limited companies. Models HMRC's post-April 2023 merged scheme and the R&D-intensive enhanced rate (ERIS).",
    path: "/calculators/rd-tax-credit-estimator",
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
              { label: "R&D Tax Credit Estimator" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free calculator · 2025/26 merged scheme
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              R&amp;D Tax Credit Estimator
            </h1>
            <p className="mt-4 text-lg text-slate-300">
              Get a directional estimate of your R&D tax credit using HMRC's post-April 2023 merged scheme rules, including the R&D-intensive enhanced rate.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <RDCreditEstimator />

            <div className="mt-12 bg-slate-900 p-8 sm:p-10 text-white">
              <h2 className="text-2xl font-bold text-white sm:text-3xl">Want us to assess your actual claim?</h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200">
                We've processed R&D claims for AI, SaaS, software, engineering, manufacturing and innovation-led service businesses into six figures. Book a free call and we'll review your projects for genuine qualifying activity.
              </p>
              <Link href="/free-health-check" className="mt-6 inline-block bg-orange-600 px-8 py-3 font-bold text-white border-b-4 border-orange-800 hover:bg-orange-700 transition-all">
                Book a free assessment
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
