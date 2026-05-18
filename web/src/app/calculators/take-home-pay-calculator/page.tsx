import type { Metadata } from "next";
import Link from "next/link";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { TakeHomePayCalculator } from "@/components/calculators/TakeHomePayCalculator";
import { Calculator } from "lucide-react";
import { JsonLd, buildWebApplication, buildFaqPage } from "@/lib/schema";

export const metadata: Metadata = {
  title: "Take-Home Pay Calculator 2025/26 | UK Salary After Tax",
  description:
    "Free UK take-home pay calculator. 2025/26 income tax, NI, student loan and pension salary sacrifice. Annual, monthly and weekly net figures.",
  alternates: { canonical: `${siteConfig.url}/calculators/take-home-pay-calculator` },
  openGraph: {
    title: "Take-Home Pay Calculator 2025/26 | UK Salary After Tax",
    description: "Free UK take-home pay calculator. 2025/26 income tax, NI, student loan and pension salary sacrifice.",
    url: `${siteConfig.url}/calculators/take-home-pay-calculator`,
    type: "website",
  },
};

const faqs = [
  {
    q: "What's in 2025/26 take-home pay?",
    a: "For a UK employee: gross salary, minus income tax (20% basic, 40% higher, 45% additional), minus employee National Insurance (8% between £12,570 and £50,270, 2% above), minus any student loan deductions, minus any salary-sacrifice pension contribution. The personal allowance is £12,570 and tapers by £1 for every £2 of income above £100,000, fully gone at £125,140.",
  },
  {
    q: "How does salary sacrifice pension affect take-home pay?",
    a: "Salary sacrifice reduces your gross salary by the contribution amount before income tax and NI are calculated, so you save income tax AND NI on the sacrificed amount. The contribution goes straight into your pension. This is more tax-efficient than a relief-at-source contribution because you also get NI relief, which a standard contribution doesn't give you.",
  },
  {
    q: "Which student loan plan am I on?",
    a: "Plan 1 if you started uni before September 2012 in England/Wales (threshold £24,990, 9%). Plan 2 if you started Sept 2012 – Aug 2023 in England/Wales (£27,295, 9%). Plan 4 for Scottish loans (£31,395, 9%). Plan 5 for England loans from August 2023 (£25,000, 9%). Postgraduate loan is separate and charged at 6% above £21,000, it stacks on top of any undergraduate plan.",
  },
  {
    q: "Does this work for limited company directors?",
    a: "Only partly. If you run a limited company and pay yourself a small salary plus dividends, this calculator covers just the salary portion. For the full picture across salary + dividend + corporation tax, use our Salary & Dividend Optimiser instead.",
  },
];

export default function TakeHomePayCalculatorPage() {
  const webApp = buildWebApplication({
    name: "Take-Home Pay Calculator 2025/26",
    description: "Free UK take-home pay calculator: 2025/26 income tax, NI, student loan and pension salary sacrifice. Annual, monthly and weekly net figures.",
    path: "/calculators/take-home-pay-calculator",
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
              { label: "Take-Home Pay Calculator" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free calculator · 2025/26 rates
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Take-Home Pay Calculator
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              The HMRC headline number says one thing, what arrives in your account says another. Enter your gross salary and the calculator returns annual, monthly and weekly net pay for 2025/26, with income tax, employee NI, student loan plans, and any salary-sacrifice pension contributions all factored in.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <TakeHomePayCalculator />

            <div className="mt-12 border-l-4 border-orange-600 bg-slate-50 p-6 sm:p-8">
              <h2 className="text-xl font-bold text-slate-900">How this works</h2>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                The calculator applies the standard 2025/26 personal allowance of £12,570 (tapering above £100,000), the three income tax bands, and employee NI at 8% on earnings between £12,570 and £50,270 plus 2% above. Salary-sacrifice pension contributions are deducted before tax and NI are calculated, so they save you both. Student loan deductions are added if you select a plan.
              </p>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                The model assumes a standard tax code (1257L), no taxable benefits in kind, no other income, and that you are paid through PAYE.
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
                Drawing dividends from your own Ltd? This calculator misses half the picture
              </h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200 leading-relaxed">
                Limited company owners typically take a small PAYE salary alongside dividends from post-tax profit. The take-home pay calculator handles the salary leg only. To see the full position, use the salary &amp; dividend optimiser, which prices corporation tax and dividend tax into the same model.
              </p>
              <Link
                href="/calculators/salary-dividend-optimiser"
                className="mt-6 inline-block bg-orange-600 px-8 py-3 text-base font-bold text-white border-b-4 border-orange-800 hover:bg-orange-700 hover:border-orange-900 transition-all"
              >
                Open the optimiser
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
