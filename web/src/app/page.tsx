import type { Metadata } from "next";
import Link from "next/link";
import { btnPrimary, btnSecondary, siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { JsonLd, buildOrganization, buildWebSite } from "@/lib/schema";
import { buildFaqPage } from "@/lib/schema/faq-page";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { SignupForm } from "@/components/newsletter/SignupForm";
import { ArrowRight } from "lucide-react";

export const metadata: Metadata = {
  title: `${siteConfig.name} | ICAEW chartered accountants for UK business`,
  description:
    "ICAEW chartered accountants serving UK limited companies, sole traders, contractors and partnerships. Corporation tax, VAT, payroll, R&D credits, MTD, and exit planning. National coverage, fixed fees.",
  alternates: { canonical: siteConfig.url },
  openGraph: {
    title: `${siteConfig.name} | ICAEW chartered accountants for UK business`,
    description:
      "ICAEW chartered accountants for UK limited companies, sole traders, contractors and partnerships. National coverage, fixed fees.",
    url: siteConfig.url,
    type: "website",
    images: [{ url: siteConfig.publisherLogoUrl, alt: siteConfig.name }],
  },
  twitter: {
    card: "summary_large_image",
    title: `${siteConfig.name} | ICAEW chartered accountants for UK business`,
    description:
      "ICAEW chartered accountants for UK limited companies, sole traders, contractors and partnerships. National coverage, fixed fees.",
  },
};

const services = [
  {
    n: "01",
    title: "Corporation tax and year-end",
    body: "Statutory accounts and CT600 filings, marginal-relief planning between £50,000 and £250,000, director remuneration modelling.",
  },
  {
    n: "02",
    title: "VAT and Making Tax Digital",
    body: "VAT registration timing, scheme selection (Standard, Flat Rate, Cash, Annual), and the quarterly MTD discipline.",
  },
  {
    n: "03",
    title: "Payroll, PAYE and pensions",
    body: "Monthly payroll, RTI submissions, Employment Allowance, salary-sacrifice schemes and director pension contributions.",
  },
  {
    n: "04",
    title: "R&D credits and reliefs",
    body: "Merged-scheme R&D claims, capital allowances, BADR and patent-box where it applies. Technical narrative written by qualified staff.",
  },
];

const faqs = [
  {
    question: "What does the firm actually cost?",
    answer:
      "Fees depend on complexity: turnover, payroll size, VAT scheme, number of directors, R&D activity, whether you need management accounts as well as year-end. We quote a fixed fee after a short discovery call. Nothing is added without your sign-off, and the engagement letter is plain English.",
  },
  {
    question: "Do you work with sole traders and partnerships, or only limited companies?",
    answer:
      "All four UK trading structures. Sole traders, partnerships, LLPs and limited companies are all on the engagement roster. The work that applies depends on the structure: self-assessment for sole traders and partners, corporation tax and director pay for Ltds, and partnership returns where relevant.",
  },
  {
    question: "Are you ICAEW members or just registered tax agents?",
    answer:
      "Our team operates under ICAEW chartered accountancy standards. That is a deliberate floor: many UK accounting firms employ AAT-qualified bookkeepers and trade as accountants. ICAEW members hold a higher technical bar and a regulated professional code, which matters when the advice is non-obvious.",
  },
  {
    question: "How does the relationship actually work, week to week?",
    answer:
      "Cloud-first via Xero, FreeAgent or QuickBooks depending on what you already use. One named accountant on the engagement. Email and scheduled calls; ad-hoc questions answered within one working day. Annual cycle: bookkeeping handover, VAT quarters where relevant, payroll monthly, year-end, planning conversation.",
  },
];

// Composite snapshots based on patterns across our client base.
// Anonymised by structure: business type, scale, location, outcome.
// No specific clients named.
const testimonials = [
  {
    quote:
      "They flagged a marginal-relief miscalculation in our first review that had been missed for three years. Refund and reset, plus quarterly visibility we never had.",
    attribution: "Limited company, 12 staff, professional services, Bristol",
  },
  {
    quote:
      "Switching mid-year from sole trader to Ltd was the right call once they modelled it properly. About £11,000 saved in year one against a five-figure setup.",
    attribution: "Independent consultant, newly incorporated, Leeds",
  },
  {
    quote:
      "We were on Standard VAT when Flat Rate was clearly the better fit for our cost mix. Scheme review paid for itself inside a quarter.",
    attribution: "Two-director Ltd, e-commerce, Manchester",
  },
];

export default function HomePage() {
  return (
    <>
      <JsonLd
        data={[buildOrganization(), buildWebSite(), buildFaqPage(faqs)].filter(
          (s): s is NonNullable<typeof s> => s !== null,
        )}
      />

      {/* 1. HERO — typographic, off-white, no photo */}
      <section className="bg-[#fafaf7] pt-20 pb-24 sm:pt-28 sm:pb-32 lg:pt-32 lg:pb-40">
        <div className={siteContainerLg}>
          <div className="max-w-4xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              ICAEW chartered accountants
            </p>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-neutral-900 leading-[1.05] sm:text-6xl lg:text-7xl text-balance">
              UK business{" "}
              <span className="text-orange-500">accounting,</span>
              <br />
              done with conviction.
            </h1>
            <p className="mt-8 max-w-2xl text-lg leading-relaxed text-neutral-600 sm:text-xl">
              Year-round compliance and the advisory you actually want. Limited
              companies, sole traders, contractors, partnerships. One named ICAEW
              accountant. Cloud-first delivery. Fixed fees, agreed up front.
            </p>
            <div className="mt-12 flex flex-col sm:flex-row gap-3">
              <Link href="/contact" className={btnPrimary}>
                Book a free call
              </Link>
              <Link href="/services" className={btnSecondary}>
                What we cover
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 2. PROOF BAND — hairlines, Geist Mono numbers */}
      <section className="border-y border-neutral-200 bg-[#fafaf7]">
        <div className={siteContainerLg}>
          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-neutral-200">
            {[
              { value: "ICAEW", label: "Chartered network" },
              { value: "100+", label: "UK businesses served" },
              { value: "24h", label: "Response window" },
              { value: "Fixed", label: "Fee, never hourly" },
            ].map((stat, i) => (
              <div
                key={i}
                className={`py-10 sm:py-12 px-6 ${i === 0 ? "pl-0" : ""} ${i === 3 ? "pr-0" : ""}`}
              >
                <div className="font-mono text-3xl sm:text-4xl font-medium tracking-tight text-neutral-900">
                  {stat.value}
                </div>
                <div className="mt-3 text-xs font-medium uppercase tracking-wider text-neutral-500">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. WHAT WE DO — numbered editorial list */}
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <div className="grid lg:grid-cols-[1fr_2fr] gap-12 lg:gap-20">
            <div>
              <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                Practice
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl lg:text-5xl">
                What the engagement covers.
              </h2>
              <p className="mt-6 text-base leading-relaxed text-neutral-600">
                Compliance is table stakes. The work that pays for itself is the
                advisory that sits on top: pay structures, VAT scheme choice, R&amp;D
                claims, capital allowances, succession planning.
              </p>
            </div>
            <div>
              <ul className="divide-y divide-neutral-200 border-t border-neutral-200">
                {services.map((s) => (
                  <li key={s.n} className="py-8 grid grid-cols-[3rem_1fr] gap-6">
                    <div className="font-mono text-sm font-medium text-orange-500 pt-1">
                      {s.n}
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold tracking-tight text-neutral-900">
                        {s.title}
                      </h3>
                      <p className="mt-2 text-base leading-relaxed text-neutral-600 max-w-xl">
                        {s.body}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 4. WHO WE WORK WITH — single typographic statement, no tiles */}
      <section className={`${sectionY} bg-neutral-900 text-white`}>
        <div className={siteContainerLg}>
          <p className="font-mono text-xs uppercase tracking-widest text-orange-400">
            Coverage
          </p>
          <div className="mt-8 text-4xl font-semibold tracking-tight leading-[1.05] sm:text-6xl lg:text-7xl max-w-5xl">
            <span>Limited companies.</span>
            <span className="text-orange-400 mx-3">·</span>
            <span>Sole traders.</span>
            <span className="text-orange-400 mx-3">·</span>
            <span>Contractors.</span>
            <span className="text-orange-400 mx-3">·</span>
            <span>Partnerships.</span>
          </div>
          <p className="mt-10 max-w-2xl text-lg leading-relaxed text-neutral-400">
            From a first incorporation decision through to a nine-figure exit.
            Cloud-first, nationally available, ICAEW-qualified, fixed-fee.
          </p>
        </div>
      </section>

      {/* 5. EDITORIAL PULL-QUOTES — stacked, large italic, mono attribution */}
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <div className="max-w-4xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500 mb-4">
              In practice
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl lg:text-5xl">
              What the work has produced.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-neutral-600 max-w-2xl">
              Composite snapshots based on patterns across our client base. Names
              and figures anonymised. The mechanics are real.
            </p>
          </div>
          <div className="mt-16 divide-y divide-neutral-200 border-t border-neutral-200">
            {testimonials.map((t, i) => (
              <figure key={i} className="py-12 grid grid-cols-1 lg:grid-cols-[3rem_1fr] gap-6 lg:gap-10">
                <div className="font-mono text-orange-500 text-5xl leading-none -mt-2" aria-hidden>
                  &ldquo;
                </div>
                <div>
                  <blockquote className="text-2xl sm:text-3xl font-medium italic leading-[1.3] tracking-tight text-neutral-900 max-w-3xl">
                    {t.quote}
                  </blockquote>
                  <figcaption className="mt-6 font-mono text-xs uppercase tracking-widest text-neutral-500">
                    {t.attribution}
                  </figcaption>
                </div>
              </figure>
            ))}
          </div>
        </div>
      </section>

      {/* 6. MANIFESTO BLOCK — short typographic statement */}
      <section className={`${sectionY} bg-[#fafaf7] border-t border-neutral-200`}>
        <div className={siteContainerLg}>
          <div className="max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              Position
            </p>
            <p className="mt-6 text-2xl sm:text-3xl lg:text-4xl font-medium tracking-tight leading-[1.25] text-neutral-900">
              Most UK firms compete on{" "}
              <span className="text-orange-500">price</span>. The ones worth hiring
              compete on the cost of the advice you did <em>not</em> get. We work to
              the second standard.
            </p>
          </div>
        </div>
      </section>

      {/* 7. NEWSLETTER — small card, single field, orange button */}
      <section className={`${sectionY} bg-white border-t border-neutral-200`}>
        <div className={siteContainerLg}>
          <div className="max-w-2xl">
            <SignupForm
              source="homepage-mid"
              variant="card"
              heading="The Director's Brief"
              body="One short note a week for UK business owners. Tax, structure, payroll, cash. Plain text, one CTA, unsubscribe in one click."
              ctaLabel="Subscribe"
            />
          </div>
        </div>
      </section>

      {/* 8. CTA — light, big H2, single primary button to /contact */}
      <section className={`${sectionY} bg-[#fafaf7] border-t border-neutral-200`}>
        <div className={siteContainerLg}>
          <div className="grid lg:grid-cols-[2fr_1fr] gap-12 items-center">
            <div>
              <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                Get started
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl lg:text-5xl text-balance">
                Talk to an ICAEW accountant. Free, no obligation.
              </h2>
              <p className="mt-6 max-w-xl text-base leading-relaxed text-neutral-600">
                Tell us briefly where the business sits today. We&apos;ll come back
                with a short note on what the engagement would look like and what it
                would cost. No pitch deck, no follow-up sequence.
              </p>
            </div>
            <div className="flex lg:justify-end">
              <Link href="/contact" className={btnPrimary}>
                Book a free call
                <ArrowRight className="ml-2 h-4 w-4" aria-hidden />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 9. FAQ — restyled Accordion */}
      <section className={`${sectionY} bg-[#fafaf7] border-t border-neutral-200`}>
        <div className={siteContainerLg}>
          <div className="grid lg:grid-cols-[1fr_2fr] gap-12 lg:gap-20">
            <div>
              <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                Common questions
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl">
                The honest answers.
              </h2>
            </div>
            <div>
              <Accordion type="single" collapsible className="border-t border-neutral-200">
                {faqs.map((item, i) => (
                  <AccordionItem key={item.question} value={`faq-${i}`}>
                    <AccordionTrigger>{item.question}</AccordionTrigger>
                    <AccordionContent>
                      <p>{item.answer}</p>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
