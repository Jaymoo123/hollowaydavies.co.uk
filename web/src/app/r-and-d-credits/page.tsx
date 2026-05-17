import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import {
  ArrowRight,
  BadgeCheck,
  Beaker,
  Bot,
  Calculator,
  ClipboardCheck,
  Code,
  Cpu,
  FileSearch,
  LineChart,
} from "lucide-react";
import { siteContainerLg, btnPrimary, btnSecondary } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { LeadForm } from "@/components/forms/LeadForm";
import { JsonLd, buildService, buildFaqPage } from "@/lib/schema";

export const metadata: Metadata = {
  title: "R&D Tax Credits for UK Businesses | Specialist Claims",
  description:
    "Specialist R&D tax credit claims for UK companies. Software, AI, engineering, manufacturing, biotech, food tech. Most claims leave money on the table. ICAEW qualified, no-win-no-fee available.",
  alternates: { canonical: `${siteConfig.url}/r-and-d-credits` },
  openGraph: {
    title: "R&D Tax Credits for UK Businesses",
    description: "Specialist R&D tax credit claims for UK companies. ICAEW qualified.",
    url: `${siteConfig.url}/r-and-d-credits`,
    type: "website",
  },
};

const qualifying = [
  {
    icon: Bot,
    title: "AI and machine learning",
    body: "Custom model training, RAG pipelines, fine-tuning LLMs for specific industries, agent orchestration, novel ML architectures. Average claim: £40k-£150k+.",
  },
  {
    icon: Code,
    title: "Software and SaaS",
    body: "Custom architecture, novel integrations, performance optimisations beyond published benchmarks, bespoke developer tooling and platform engineering.",
  },
  {
    icon: Cpu,
    title: "Engineering and product development",
    body: "Mechanical, electrical and electronic product design where the solution wasn't obvious to a competent professional. Prototyping, testing, iterative redesign.",
  },
  {
    icon: Beaker,
    title: "Manufacturing and process improvement",
    body: "Novel materials, production process improvements that resolve technical uncertainty, automation builds, quality control systems beyond off-the-shelf.",
  },
  {
    icon: LineChart,
    title: "Custom software development",
    body: "Custom CMS architecture, headless commerce builds, novel integrations between systems with no off-the-shelf connectors, performance-critical infrastructure.",
  },
  {
    icon: FileSearch,
    title: "Biotech, food tech and scientific R&D",
    body: "Formulation work, process science, novel testing methods, scientific advance in a recognised field. Lab work, trials, iterative experimentation.",
  },
];

const process = [
  { n: "01", title: "Eligibility assessment", body: "30-min call. We review your projects against HMRC's qualifying activity tests. Most companies have more eligible work than they think." },
  { n: "02", title: "Project scoping", body: "We identify which specific projects qualify, apportion staff time, and quantify subcontractor and cloud costs. Done in 1-2 weeks." },
  { n: "03", title: "Claim preparation", body: "Full technical narrative + costing schedule. Built to HMRC's current standards, with proper documentation that holds up under enquiry." },
  { n: "04", title: "Submission & monitoring", body: "We submit, monitor HMRC processing, and handle any questions. Most claims pay out within 8-12 weeks." },
];

const faqs = [
  {
    q: "Does my company actually qualify?",
    a: "More companies qualify than realise. The test is whether your work involves resolving genuine scientific or technological uncertainty, building something where a competent professional couldn't have just looked up the answer. Custom AI work, novel integrations, bespoke automation, engineering breakthroughs, process science all typically qualify. Pure configuration of off-the-shelf tools, template customisation and standard implementations do not. We assess for free.",
  },
  {
    q: "What's the typical claim size?",
    a: "Highly variable. AI-led companies with 4-8 engineers commonly claim £40k-£150k per year. SaaS, software and engineering companies building proprietary tooling typically claim £15k-£60k. Smaller companies doing some custom development or process improvement might claim £5k-£20k. The R&D-intensive enhanced rate (27% vs 20%) can lift these significantly.",
  },
  {
    q: "What changed with the merged scheme in April 2024?",
    a: "For accounting periods starting on or after 1 April 2024, the old SME and RDEC schemes were merged into one above-the-line credit at 20% of qualifying expenditure. R&D-intensive SMEs (where R&D spend is 30%+ of total expenditure and the company is loss-making) get the Enhanced R&D Intensive Support (ERIS) scheme. Subcontractor costs are claimable at 65%. The PAYE-NI cap may apply to limit claims for businesses with low payroll relative to claim size.",
  },
  {
    q: "Do you charge a percentage of the claim?",
    a: "We offer two options: fixed fee or contingent (percentage of successful claim, capped). Most clients prefer the fixed fee because the total cost is lower for substantive claims, but the contingent option works well for first-time claimants who want no upfront risk. We discuss both on the initial call.",
  },
  {
    q: "How long does a claim take to process at HMRC?",
    a: "HMRC's stated processing time is 40 working days for the merged scheme, though it's currently averaging 8-12 weeks. Enquiry rates have risen significantly since the 2023-24 reforms, so the quality of your technical narrative and costing schedule matters more than ever. We build claims to current HMRC standards.",
  },
];

export default function RDPage() {
  const service = buildService({
    name: "R&D Tax Credit Claims for UK Companies",
    description:
      "Specialist R&D tax credit claim preparation for UK companies. Software, AI, engineering, manufacturing, biotech, food tech and innovation-led services.",
    url: "/r-and-d-credits",
    serviceType: "R&D tax credit claim preparation",
    areaServed: "United Kingdom",
  });
  const faqPage = buildFaqPage(faqs.map((f) => ({ question: f.q, answer: f.a })));

  return (
    <>
      <JsonLd data={faqPage ? [service, faqPage] : [service]} />

      <section className="relative h-[480px] sm:h-[540px] overflow-hidden">
        <Image
          src="https://images.unsplash.com/photo-1581090464777-f3220bbe1b8b?w=2000&q=85"
          alt="Engineer at work with code on screens"
          fill
          priority
          sizes="100vw"
          className="object-cover brightness-50"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950/95 via-slate-900/90 to-slate-900/60" />
        <div className={`${siteContainerLg} relative z-10 h-full flex items-end pb-12 sm:pb-16`}>
          <div className="max-w-3xl">
            <Breadcrumb
              variant="light"
              items={[
                { label: "Home", href: "/" },
                { label: "R&D Tax Credits" },
              ]}
            />
            <div className="mt-6 inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <Beaker className="h-3.5 w-3.5" />
              Specialist R&D claims · Merged scheme + ERIS
            </div>
            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-bold leading-tight text-white">
              R&amp;D tax credits for <span className="text-orange-400">UK companies</span>
            </h1>
            <p className="mt-4 text-lg sm:text-xl text-slate-200 max-w-2xl">
              Most UK companies doing custom development, novel engineering or process science qualify for R&D tax credits and don't claim them. We've processed claims from £15k to over £150k for software, AI, engineering, manufacturing and biotech businesses.
            </p>
            <div className="mt-6 flex flex-wrap gap-3 sm:gap-4">
              <Link href="#assessment" className={`${btnPrimary} text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4`}>
                Book a free eligibility check
              </Link>
              <Link href="/calculators/rd-tax-credit-estimator" className={`${btnSecondary} bg-white/10 border-white text-white hover:bg-white/20 text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4`}>
                Try the calculator
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-orange-700 py-8 sm:py-10">
        <div className={siteContainerLg}>
          <div className="grid grid-cols-2 gap-6 sm:gap-8 md:grid-cols-4">
            {[
              { v: "20%", l: "Standard merged scheme rate" },
              { v: "27%", l: "ERIS enhanced rate" },
              { v: "65%", l: "Subcontractor cost claimable" },
              { v: "£15k-£150k+", l: "Typical claim range" },
            ].map((s) => (
              <div key={s.l} className="text-center">
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white font-mono">{s.v}</div>
                <div className="mt-1.5 text-xs sm:text-sm font-semibold text-orange-200 uppercase tracking-wider">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12 max-w-3xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">Which companies typically qualify?</h2>
              <p className="mt-4 text-lg text-slate-600">
                Six business types where we see consistent qualifying R&D activity. If your team builds custom tech, novel products or improved processes, you're likely sitting on an unclaimed credit.
              </p>
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {qualifying.map((q) => {
                const Icon = q.icon;
                return (
                  <div key={q.title} className="bg-slate-50 border border-slate-200 p-6 sm:p-7 hover:bg-white hover:border-orange-600 hover:shadow-md transition-all">
                    <div className="flex items-center justify-center h-12 w-12 bg-gradient-to-br from-orange-500 to-orange-700 shadow-sm">
                      <Icon className="h-6 w-6 text-white" strokeWidth={2} />
                    </div>
                    <h3 className="mt-5 text-lg font-bold text-slate-900">{q.title}</h3>
                    <p className="mt-3 text-sm leading-relaxed text-slate-600">{q.body}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="bg-slate-50 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12 max-w-3xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">How our R&D claims process works</h2>
              <p className="mt-4 text-lg text-slate-600">
                Four steps from initial assessment to HMRC payment. Most claims complete in 12-16 weeks total.
              </p>
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {process.map((s) => (
                <div key={s.n} className="bg-white border-l-4 border-orange-600 p-6 sm:p-7">
                  <div className="font-mono text-3xl font-bold text-orange-600">{s.n}</div>
                  <h3 className="mt-3 text-lg font-bold text-slate-900">{s.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">{s.body}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <div className="bg-orange-50 border-2 border-orange-600 p-8 sm:p-10 text-center">
              <Calculator className="h-12 w-12 text-orange-600 mx-auto mb-4" />
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Get a directional estimate first</h2>
              <p className="mt-3 text-base sm:text-lg text-slate-700">
                Use our free R&D Tax Credit Estimator to see roughly what your claim could be worth before talking to us.
              </p>
              <Link href="/calculators/rd-tax-credit-estimator" className="mt-6 inline-flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-8 py-3 font-bold transition-colors">
                Open the calculator
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section id="assessment" className="bg-white py-16 sm:py-20 border-t border-slate-200">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <div className="bg-orange-50 border-2 border-orange-600/20 p-8 sm:p-12">
              <div className="text-center mb-8">
                <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
                  <ClipboardCheck className="h-3.5 w-3.5" />
                  Free 30-min eligibility check
                </div>
                <h2 className="text-3xl font-bold text-orange-900 sm:text-4xl">
                  Book a free R&D eligibility check
                </h2>
                <p className="mt-3 text-base sm:text-lg text-slate-700">
                  We review your projects against HMRC's qualifying activity tests. You leave with a clear yes/no and a directional estimate of claim size.
                </p>
              </div>
              <LeadForm redirectOnSuccess={false} submitLabel="Book my R&D eligibility check" />
              <p className="mt-4 text-xs text-slate-500 text-center">
                In the message field, please describe the type of custom development, engineering or process work your company does.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-slate-50 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl mb-8 text-center">
              R&D credit FAQ
            </h2>
            <div className="space-y-4">
              {faqs.map((f) => (
                <div key={f.q} className="bg-white border-l-4 border-slate-300 hover:border-orange-600 transition-all p-6">
                  <h3 className="text-lg font-bold text-slate-900">{f.q}</h3>
                  <p className="mt-3 text-base text-slate-700 leading-relaxed">{f.a}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="bg-slate-900 py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto text-center">
            <BadgeCheck className="h-12 w-12 text-orange-400 mx-auto mb-4" />
            <h2 className="text-2xl sm:text-3xl font-bold text-white">
              Read the R&D library
            </h2>
            <p className="mt-4 text-slate-300 max-w-2xl mx-auto">
              Articles on R&D tax credit eligibility, claim mechanics, sector-specific qualifying activities and HMRC edge cases.
            </p>
            <Link
              href="/blog/r-and-d-tax-credits"
              className="mt-6 inline-flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-8 py-3 font-bold transition-colors"
            >
              Browse R&D articles
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
