import type { Metadata } from "next";
import Link from "next/link";
import { siteContainerLg, sectionY, btnPrimary, btnSecondary } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { JsonLd, buildOrganization } from "@/lib/schema";

export const metadata: Metadata = {
  title: `About`,
  description: `${siteConfig.name} is an ICAEW chartered accountancy practice serving UK limited companies, sole traders, contractors and partnerships. National coverage, fixed fees, plain-English advice.`,
  alternates: { canonical: `${siteConfig.url}/about` },
  openGraph: {
    title: `About | ${siteConfig.name}`,
    description: "ICAEW chartered accountants for UK businesses of every shape.",
    url: `${siteConfig.url}/about`,
    type: "website",
  },
};

const principles = [
  {
    n: "01",
    title: "Compliance is table stakes.",
    body: "Filing year-end accounts on time is the floor, not the ceiling. The work that pays for itself is the advisory that sits on top: pay structures, scheme selection, capital allowances, R&D claims, succession planning, exit timing. We bill for that work, not for filing.",
  },
  {
    n: "02",
    title: "Credentials matter, plainly.",
    body: "We operate to ICAEW chartered accountancy standards. That&rsquo;s a deliberate technical floor. Many UK firms employ AAT-qualified bookkeepers and trade as accountants; the work doesn&rsquo;t always read the same.",
  },
  {
    n: "03",
    title: "One named accountant.",
    body: "You speak to the same accountant every time. No call-centre routing, no junior handoffs. Fixed fees agreed up front in writing, no surprises, no hourly billing on questions.",
  },
  {
    n: "04",
    title: "Cloud-first, country-wide.",
    body: "Xero, FreeAgent or QuickBooks depending on what you already use. Everything else runs on email and scheduled calls. Local presence has stopped mattering for accounting; competence and responsiveness haven&rsquo;t.",
  },
];

const principlesAlt = [
  {
    label: "Who",
    body: "Limited company directors, contractors and freelancers, sole traders, and partnerships across every UK sector.",
  },
  {
    label: "Where",
    body: "Nationwide. Cloud-first delivery means London, Leeds, Glasgow and Bristol clients get the same response time.",
  },
  {
    label: "How",
    body: "Annual cycle of bookkeeping handover, quarterly VAT where relevant, monthly payroll, year-end, plus a planning conversation that sits outside the compliance cycle.",
  },
  {
    label: "Why",
    body: "Most UK firms compete on price. The ones worth hiring compete on the cost of the advice you didn&rsquo;t get.",
  },
];

export default function AboutPage() {
  return (
    <>
      <JsonLd data={buildOrganization()} />

      {/* Hero */}
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <div className="max-w-4xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              About
            </p>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-neutral-900 leading-[1.05] sm:text-6xl lg:text-7xl text-balance">
              A modern firm,{" "}
              <span className="text-orange-500">classically qualified.</span>
            </h1>
            <p className="mt-8 max-w-2xl text-lg leading-relaxed text-neutral-600 sm:text-xl">
              {siteConfig.name} is an ICAEW chartered accountancy practice for UK
              business owners. We cover the four trading structures (limited
              company, sole trader, contractor, partnership) across every sector,
              with the depth a specialist firm would bring and the responsiveness
              an in-house team would expect.
            </p>
          </div>
        </div>
      </section>

      {/* Principles */}
      <section className={`${sectionY} bg-[#fafaf7] border-t border-neutral-200`}>
        <div className={siteContainerLg}>
          <div className="grid lg:grid-cols-[1fr_2fr] gap-12 lg:gap-20">
            <div>
              <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                What we believe
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl lg:text-5xl">
                Four operating principles.
              </h2>
            </div>
            <div>
              <ul className="divide-y divide-neutral-200 border-t border-neutral-200">
                {principles.map((p) => (
                  <li key={p.n} className="py-8 grid grid-cols-[3rem_1fr] gap-6">
                    <div className="font-mono text-sm font-medium text-orange-500 pt-1">
                      {p.n}
                    </div>
                    <div>
                      <h3
                        className="text-xl font-semibold tracking-tight text-neutral-900"
                        dangerouslySetInnerHTML={{ __html: p.title }}
                      />
                      <p
                        className="mt-3 text-base leading-relaxed text-neutral-600 max-w-xl"
                        dangerouslySetInnerHTML={{ __html: p.body }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Quick facts */}
      <section className={`${sectionY} bg-neutral-900 text-white`}>
        <div className={siteContainerLg}>
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
            {principlesAlt.map((item) => (
              <div key={item.label}>
                <p className="font-mono text-xs uppercase tracking-widest text-orange-400">
                  {item.label}
                </p>
                <p
                  className="mt-4 text-lg leading-relaxed text-neutral-200"
                  dangerouslySetInnerHTML={{ __html: item.body }}
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Editorial standards */}
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <div className="grid lg:grid-cols-[1fr_2fr] gap-12 lg:gap-20">
            <div>
              <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                Editorial
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl">
                On what you read here.
              </h2>
            </div>
            <div className="prose-blog max-w-2xl">
              <p>
                Every figure on this site uses 2025/26 UK tax rates and is
                traceable to a primary source: HMRC, Companies House, ICAEW
                guidance, or the relevant statute. Where rates are scheduled to
                change, we say so and date the change.
              </p>
              <p>
                Articles on this site are <strong>editorial</strong>, not advice.
                They explain mechanics; they don&rsquo;t apply them to your specific
                circumstances. For advice that fits, book a call. There&rsquo;s no
                pitch and no obligation; if we&rsquo;re not a fit we&rsquo;ll say so
                quickly.
              </p>
              <p>
                Found a mistake, an out-of-date figure or an unclear paragraph?{" "}
                <a href={`mailto:${siteConfig.contact.email}`}>Email the editorial team</a>
                {" "}and we&rsquo;ll fix it.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className={`${sectionY} bg-[#fafaf7] border-t border-neutral-200`}>
        <div className={siteContainerLg}>
          <div className="grid lg:grid-cols-[2fr_1fr] gap-12 items-center">
            <div>
              <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                Next step
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl lg:text-5xl text-balance">
                Have a short call with an accountant.
              </h2>
              <p className="mt-6 max-w-xl text-base leading-relaxed text-neutral-600">
                Tell us where the business sits today. We&rsquo;ll come back with a
                plain note on what the engagement would look like and what it
                would cost.
              </p>
            </div>
            <div className="flex flex-col gap-3 lg:items-end">
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
    </>
  );
}
