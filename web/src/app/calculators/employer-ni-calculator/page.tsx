import type { Metadata } from "next";
import Link from "next/link";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { EmployerNICalculator } from "@/components/calculators/EmployerNICalculator";
import { Calculator } from "lucide-react";
import { JsonLd, buildWebApplication, buildFaqPage } from "@/lib/schema";

export const metadata: Metadata = {
  title: "Employer NI & Cost-to-Hire Calculator 2025/26 | UK Business",
  description:
    "Free calculator: total cost of an employee in 2025/26. Employer NI at 15%, Employment Allowance £10,500, minimum pension. For UK limited companies and small businesses.",
  alternates: { canonical: `${siteConfig.url}/calculators/employer-ni-calculator` },
  openGraph: {
    title: "Employer NI & Cost-to-Hire Calculator 2025/26",
    description: "Free calculator: total cost of an employee in 2025/26. For UK businesses.",
    url: `${siteConfig.url}/calculators/employer-ni-calculator`,
    type: "website",
  },
};

const faqs = [
  {
    q: "How is employer National Insurance calculated for 2025/26?",
    a: "Employer NI (Class 1 secondary) is 15% on earnings above the secondary threshold of £5,000 per year per employee for 2025/26 (the rate increased from 13.8% and the threshold reduced from £9,100 in the Autumn Budget 2024). So an employee on £40,000 generates (£40,000 - £5,000) × 15% = £5,250 of employer NI before any Employment Allowance is applied.",
  },
  {
    q: "What is the Employment Allowance and do I qualify?",
    a: "Employment Allowance lets eligible UK employers reduce their employer NI bill by up to £10,500 per tax year in 2025/26 (up from £5,000 in 2024/25). Most small businesses qualify, but there is one critical catch: a single-director-only company (no other employees on payroll above the secondary threshold) does NOT qualify. You need at least one other paid employee. The £100,000 previous-year NI bill cap was removed from 6 April 2025, so it now applies to most employers.",
  },
  {
    q: "What about pension auto-enrolment?",
    a: "If an employee earns more than £10,000 and is aged 22 to state pension age, you must auto-enrol them and contribute at least 3% on qualifying earnings (the slice between £6,240 and £50,270). They contribute at least 5%. The calculator's pension line shows the minimum 3% employer cost only; many employers offer higher matches as part of a competitive package.",
  },
  {
    q: "What costs are not included?",
    a: "The real all-in cost of a hire is typically 10-20% higher than the salary + NI + pension figure. Things to add: software per seat (Slack, Google Workspace, Xero seat), equipment refresh, training and conferences, recruitment fees if you use a recruiter, professional memberships, private health if offered, and any bonus or commission structure. The calculator gives you the statutory floor.",
  },
];

export default function EmployerNICalculatorPage() {
  const webApp = buildWebApplication({
    name: "Employer NI & Cost-to-Hire Calculator 2025/26",
    description: "Free UK calculator: total cost of an employee in 2025/26 including employer NI, Employment Allowance and minimum auto-enrolment pension.",
    path: "/calculators/employer-ni-calculator",
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
              { label: "Employer NI Calculator" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Calculator className="h-3.5 w-3.5" />
              Free calculator · 2025/26 rates
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Employer NI &amp; cost-to-hire calculator
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              Hiring is rarely as cheap as the offer letter implies. Add a salary in, get the full employer NI at 15%, the Employment Allowance offset of up to £10,500, and the 3% auto-enrolment pension contribution stacked on top, so you can see what an extra head actually costs each month.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <EmployerNICalculator />

            <div className="mt-12 border-l-4 border-orange-600 bg-slate-50 p-6 sm:p-8">
              <h2 className="text-xl font-bold text-slate-900">How this works</h2>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                Add each role on your payroll with its gross salary. The calculator works out employer NI per employee at 15% above the £5,000 secondary threshold, applies the £10,500 Employment Allowance once across the team if you qualify, and optionally adds the minimum 3% employer pension contribution on qualifying earnings. The total annual employment cost is shown at the top.
              </p>
              <p className="mt-3 text-base text-slate-700 leading-relaxed">
                The figures are statutory floors. Real all-in cost per hire is typically 10-20% higher once you factor in software, equipment, training, recruitment and any bonus or commission structure.
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
                Budgeting a hiring round?
              </h2>
              <p className="mt-3 text-base sm:text-lg text-slate-200 leading-relaxed">
                The calculator gives you a per-role number. The harder question is sequencing: who first, how the cash flow handles it, when the Employment Allowance gets used up, and what the all-in cost looks like layered over a 12-month plan. We model that with limited company directors monthly, and the conversation is free.
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
