import type { Metadata } from "next";
import Link from "next/link";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { SalaryDividendCalculator } from "@/components/calculators/SalaryDividendCalculator";
import { Calculator } from "lucide-react";
import { JsonLd, buildWebApplication, buildFaqPage } from "@/lib/schema";

export const metadata: Metadata = {
  title: "Salary & Dividend Optimiser 2025/26 | Free UK Calculator",
  description:
    "Free salary vs dividend calculator for UK limited company directors. Optimal split using 2025/26 tax rates. Built by ICAEW accountants.",
  alternates: { canonical: `${siteConfig.url}/calculators/salary-dividend-optimiser` },
  openGraph: {
    title: "Salary & Dividend Optimiser 2025/26 | Free UK Calculator",
    description:
      "Find the most tax-efficient mix of salary and dividends for a UK limited company director. Free, no sign-up.",
    url: `${siteConfig.url}/calculators/salary-dividend-optimiser`,
    type: "website",
  },
};

const faqs = [
  {
    q: "What rates does this calculator use?",
    a: "UK 2025/26 tax year rates. Personal allowance £12,570. Basic rate 20% (£12,571-£50,270). Higher rate 40% (£50,271-£125,140). Additional rate 45% (above £125,140). Dividend rates 8.75% basic, 33.75% higher, 39.35% additional. Dividend allowance £500. Employer NI 15% above secondary threshold (£5,000). Employee NI 8% above primary threshold (£12,570). Corporation tax 19% small profits, 25% main rate.",
  },
  {
    q: "Does it cover the marginal corporation tax rate?",
    a: "Yes. For company profits between £50,000 and £250,000, marginal relief applies giving an effective rate of 26.5% on the slice between those thresholds. The calculator applies this correctly when modelling the corporation tax impact of paying salary vs dividend.",
  },
  {
    q: "Is the result personal tax advice?",
    a: "No. This is a model based on standard 2025/26 thresholds. It assumes no other income, no student loans, no pension contributions and standard UK personal allowance. For advice specific to your situation, book a free call with our team.",
  },
  {
    q: "How does taking salary vs dividends affect corporation tax?",
    a: "Salary is a deductible business expense that reduces taxable profit, so it reduces corporation tax. Dividends are paid from post-tax profits, so they don't reduce corporation tax. The optimiser models both effects together to find the true net position.",
  },
];

export default function SalaryDividendCalculatorPage() {
  const webApp = buildWebApplication({
    name: "Salary & Dividend Optimiser 2025/26",
    description: "Free UK calculator finding the most tax-efficient mix of salary and dividends for a limited company director. 2025/26 rates.",
    path: "/calculators/salary-dividend-optimiser",
    applicationCategory: "FinanceApplication",
  });
  const faqPage = buildFaqPage(faqs.map((f) => ({ question: f.q, answer: f.a })));

  return (
    <>
      <JsonLd data={faqPage ? [webApp, faqPage] : [webApp]} />

      <section className="bg-slate-900 py-12 sm:py-16">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Calculators", href: "/calculators" },
              { label: "Salary & Dividend Optimiser" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free calculator · 2025/26 rates
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Salary &amp; Dividend Optimiser
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              Pay yourself too much salary and you waste personal allowance against National Insurance. Take too much dividend and you push yourself into higher-rate dividend tax. The calculator finds the split that leaves the most money in your pocket at 2025/26 rates, accounting for corporation tax, both flavours of NI, income tax and dividend tax in one pass.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <SalaryDividendCalculator />

            <div className="mt-12 border-l-4 border-orange-600 bg-slate-50 p-6 sm:p-8">
              <h2 className="text-xl font-bold text-slate-900">How this works</h2>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                For a UK limited company director, the most tax-efficient extraction strategy typically combines a small salary (up to the primary NI threshold) with dividends drawn from post-tax profits. The calculator models corporation tax, employer NI, employee NI, income tax and dividend tax together so you see the true net position rather than each tax in isolation.
              </p>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                It assumes you have no other income, no student loan repayments, standard UK personal allowance, and no pension contributions. For a tailored model that factors in your actual position, book a free call below.
              </p>
            </div>

            <section className="mt-12">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Frequently asked questions</h2>
              <dl className="space-y-4">
                {faqs.map((f) => (
                  <div key={f.q} className="border-l-4 border-slate-300 bg-slate-50 p-6">
                    <dt className="text-lg font-bold text-slate-900">{f.q}</dt>
                    <dd className="mt-3 text-base text-slate-700 leading-relaxed">{f.a}</dd>
                  </div>
                ))}
              </dl>
            </section>

            <div className="mt-12 bg-slate-900 p-8 sm:p-10 text-white">
              <h2 className="text-2xl font-bold text-white sm:text-3xl">
                The optimum split changes with the rest of your tax picture
              </h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200 leading-relaxed">
                Add a working spouse, a buy-to-let, a student loan, a pension contribution or a planned BADR exit and the answer shifts. We build a personal extraction model for owner-managed companies that accounts for the moving parts, then revisit it each year before March.
              </p>
              <Link
                href="/contact"
                className="mt-6 inline-block bg-orange-600 px-8 py-3 text-base font-bold text-white border-b-4 border-orange-800 hover:bg-orange-700 hover:border-orange-900 transition-all"
              >
                Book a free call
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
