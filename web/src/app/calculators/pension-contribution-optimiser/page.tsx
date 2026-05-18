import type { Metadata } from "next";
import Link from "next/link";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { PensionContributionOptimiser } from "@/components/calculators/PensionContributionOptimiser";
import { Calculator } from "lucide-react";
import { JsonLd, buildWebApplication, buildFaqPage } from "@/lib/schema";

export const metadata: Metadata = {
  title: "Pension Contribution Optimiser 2025/26 | Limited Company UK",
  description:
    "Free calculator: model employer pension contributions from your UK limited company. Corp tax saving, real cost, vs taking as dividend. 2025/26 rates.",
  alternates: { canonical: `${siteConfig.url}/calculators/pension-contribution-optimiser` },
  openGraph: {
    title: "Pension Contribution Optimiser 2025/26 | Limited Company UK",
    description:
      "Free calculator: model employer pension contributions from your UK limited company.",
    url: `${siteConfig.url}/calculators/pension-contribution-optimiser`,
    type: "website",
  },
};

const faqs = [
  {
    q: "How is an employer pension contribution treated for tax?",
    a: "An employer pension contribution from your limited company is treated as an allowable business expense, it reduces your taxable profit and therefore your corporation tax bill. It's not subject to employer NI, employee NI or income tax at the point of contribution. The whole amount lands in the pension. The trade-off is that the money is locked in until you reach pension access age (currently 55, rising to 57 in April 2028).",
  },
  {
    q: "What's the annual allowance for 2025/26?",
    a: "£60,000 gross across all your pensions (employer + personal). If your 'adjusted income' (broadly salary + dividends + employer pension contributions + other income) exceeds £260,000, the annual allowance tapers by £1 for every £2 over the threshold, down to a floor of £10,000 at £360,000+. You may also be able to use carry-forward of unused allowance from the previous three tax years if you've been a pension scheme member.",
  },
  {
    q: "Is the contribution wholly and exclusively for business purposes?",
    a: "For a director who is genuinely working in the business, HMRC generally accepts an employer pension contribution as wholly and exclusively for business if it's in proportion to the work done, i.e. it could reasonably be part of an overall remuneration package. Very large contributions for a non-working spouse or in excess of total package norms can be challenged.",
  },
  {
    q: "Better to put more into salary or into pension?",
    a: "For most limited company directors paying themselves a small salary plus dividends, an employer pension contribution is more tax-efficient than the equivalent dividend at higher rate. The contribution avoids 33.75% dividend tax (or 39.35% additional) and saves corporation tax at 25%, while landing 100p of every £1 in your pension. The cost is the time delay until you can access the money.",
  },
];

export default function PensionContributionOptimiserPage() {
  const webApp = buildWebApplication({
    name: "Pension Contribution Optimiser 2025/26",
    description: "Free UK calculator: model employer pension contributions from your limited company. Corporation tax saving, real cost, vs taking as dividend.",
    path: "/calculators/pension-contribution-optimiser",
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
              { label: "Pension Contribution Optimiser" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free calculator · 2025/26 rates
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Pension Contribution Optimiser
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              For most owner-managed limited companies, pension is the most tax-efficient way to move retained profit out of the business. Plug in your numbers and the calculator shows the corporation tax saved, the net cost to the company, and how much further the same money goes versus drawing it as a dividend.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <PensionContributionOptimiser />

            <div className="mt-12 border-l-4 border-orange-600 bg-slate-50 p-6 sm:p-8">
              <h2 className="text-xl font-bold text-slate-900">How this works</h2>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                An employer pension contribution from your limited company is an allowable business expense, so it reduces your taxable profit and therefore your corporation tax. The full amount lands in your pension, no income tax, no NI. The calculator models the corporation tax saving, then compares the value of the contribution to what you'd net if you took the same money as a dividend instead.
              </p>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                It applies the 2025/26 annual allowance of £60,000 and the taper for adjusted income above £260,000. Carry-forward is not modelled, speak to us if you want to use unused allowance from previous years.
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
                A pension contribution rarely sits alone
              </h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200 leading-relaxed">
                The right number depends on your salary level, dividend extraction, retained profit, carry-forward from the last three years, and whether you are pre or post the £260,000 tapered allowance threshold. We sit with limited company directors twice a year to map that out, and the first call is on us.
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
