import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { MapPin, BadgeCheck, Phone, Mail, ArrowRight, Quote } from "lucide-react";
import { siteContainerLg, btnOnOrange } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { LeadForm } from "@/components/forms/LeadForm";
import { CITIES } from "./data";
import { JsonLd, buildAccountingService, buildFaqPage } from "@/lib/schema";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return Object.keys(CITIES).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const city = CITIES[slug];
  if (!city) return { title: "Location not found" };

  const url = `${siteConfig.url}/locations/${city.slug}`;
  // Singular "Accountant in [City]" per the primary keyword research.
  return {
    title: `Accountant in ${city.name} | ${siteConfig.name}`,
    description: `ICAEW qualified accountant in ${city.name}. Corporation tax, VAT, payroll, R&D credits, exit planning for ${city.name} limited companies, contractors and sole traders. Fixed fees, free call.`,
    alternates: {
      canonical: url,
      languages: { "en-GB": url, "x-default": url },
    },
    openGraph: {
      title: `Accountant in ${city.name}`,
      description: `ICAEW qualified accountant in ${city.name}. Fixed fees, national coverage, free initial call.`,
      url,
      type: "website",
    },
  };
}

export default async function CityPage({ params }: Props) {
  const { slug } = await params;
  const city = CITIES[slug];
  if (!city) notFound();

  // LocalBusiness / AccountingService schema with broadened areaServed and
  // sector knowledge for richer local entity signals.
  const localBusiness = buildAccountingService({
    name: `${siteConfig.name} - ${city.name}`,
    description: `ICAEW qualified accountant in ${city.name}. Corporation tax, VAT, payroll, R&D credits, exit planning. Serving limited companies, contractors, sole traders, partnerships and small businesses across ${city.region}.`,
    url: `/locations/${city.slug}`,
    city: city.name,
    address: { addressRegion: city.region },
    geo: { latitude: city.geo.latitude, longitude: city.geo.longitude },
    areaServed: [city.name, ...city.nearbyAreas],
  });
  Object.assign(localBusiness as Record<string, unknown>, {
    priceRange: "£££",
    parentOrganization: { "@type": "Organization", "@id": `${siteConfig.url}#organization` },
    serviceType: [
      "Limited company accounting",
      "Sole trader accounting",
      "Contractor accounting",
      "Tax planning",
      "Management accounts",
      "Payroll and PAYE",
      "VAT and MTD",
      "R&D tax credits",
      "Exit planning",
    ],
    knowsAbout: city.localSectors,
  });

  const faqSchema = buildFaqPage(
    city.localFaqs.map((f) => ({ question: f.question, answer: f.answer }))
  );

  return (
    <>
      <JsonLd data={faqSchema ? [localBusiness, faqSchema] : [localBusiness]} />

      {/* HERO with city photo backdrop */}
      <section className="relative h-[440px] sm:h-[520px] overflow-hidden">
        {city.heroImage ? (
          <>
            <Image
              src={city.heroImage.url}
              alt={city.heroImage.alt}
              fill
              priority
              sizes="100vw"
              className="object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-slate-950/95 via-slate-900/90 to-slate-900/60" />
          </>
        ) : (
          <div className="absolute inset-0 bg-slate-900" />
        )}
        <div className={`${siteContainerLg} relative z-10 h-full flex items-end pb-10 sm:pb-14`}>
          <div className="max-w-3xl">
            <Breadcrumb
              variant="light"
              items={[
                { label: "Home", href: "/" },
                { label: "Locations", href: "/locations" },
                { label: city.name },
              ]}
            />
            <div className="mt-6 inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <MapPin className="h-3.5 w-3.5" />
              {city.region}
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Accountant in <span className="text-orange-400">{city.name}</span>
            </h1>
            <p className="mt-4 text-lg text-slate-200 leading-relaxed max-w-2xl">
              {city.intro}
            </p>
            <div className="mt-6 flex flex-wrap gap-4 text-sm text-slate-200">
              <div className="flex items-center gap-2">
                <BadgeCheck className="h-4 w-4 text-orange-400" />
                <span className="font-semibold">ICAEW qualified</span>
              </div>
              <div className="flex items-center gap-2">
                <BadgeCheck className="h-4 w-4 text-orange-400" />
                <span className="font-semibold">Fixed fees</span>
              </div>
              <div className="flex items-center gap-2">
                <BadgeCheck className="h-4 w-4 text-orange-400" />
                <span className="font-semibold">National coverage</span>
              </div>
            </div>
          </div>
        </div>
        {city.heroImage?.photographer && (
          <p className="absolute bottom-2 right-3 z-10 text-[10px] text-slate-300/80">
            Photo:{" "}
            <a
              href={city.heroImage.photographer_url}
              target="_blank"
              rel="noopener nofollow"
              className="underline hover:text-white"
            >
              {city.heroImage.photographer}
            </a>{" "}
            /{" "}
            <a
              href={city.heroImage.pexels_url}
              target="_blank"
              rel="noopener nofollow"
              className="underline hover:text-white"
            >
              Pexels
            </a>
          </p>
        )}
      </section>

      {/* WHY HERE + BUSINESS SCENE + BUSINESS HUBS */}
      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">
              Why we work with {city.name} businesses
            </h2>
            <p className="mt-4 text-base sm:text-lg text-slate-700 leading-relaxed">{city.whyHere}</p>

            <h2 className="mt-12 text-2xl font-bold text-slate-900 sm:text-3xl">
              The {city.name} business scene
            </h2>
            <p className="mt-4 text-base sm:text-lg text-slate-700 leading-relaxed">{city.businessScene}</p>

            <div className="mt-10 bg-slate-50 border-l-4 border-orange-600 p-6">
              <p className="text-xs font-bold uppercase tracking-wider text-orange-700">
                Business hubs in {city.name}
              </p>
              <p className="mt-2 text-base text-slate-700">{city.businessHubs.join(" · ")}</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTOR EMPHASIS + KEY EMPLOYERS */}
      <section className="bg-slate-50 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-wrap gap-2 mb-6">
              {city.localSectors.map((s) => (
                <span
                  key={s}
                  className="inline-block bg-white border border-orange-200 text-orange-700 text-xs font-semibold uppercase tracking-wider px-3 py-1"
                >
                  {s}
                </span>
              ))}
            </div>
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">
              How {city.name}'s economic mix shapes our service emphasis
            </h2>
            <p className="mt-4 text-base sm:text-lg text-slate-700 leading-relaxed">
              {city.sectorEmphasis}
            </p>
            {city.keyEmployers.length > 0 && (
              <div className="mt-8 border-t border-slate-200 pt-6">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                  Anchor employers in {city.name}
                </p>
                <p className="text-base text-slate-700">
                  {city.keyEmployers.join(" · ")}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* WHAT WE DO */}
      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl mb-8">
              What we do for {city.name} businesses
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                { title: "Tax planning", body: "Salary and dividend extraction, corporation tax, R&D credits, BADR planning." },
                { title: "Management accounts", body: "Monthly P&L, cash flow forecasting, KPI dashboards." },
                { title: "Payroll & PAYE", body: "Director payroll, employee payroll, P11D benefits, RTI submissions." },
                { title: "Incorporation & structure", body: "Sole trader to limited, holding companies, alphabet shares." },
                { title: "MTD & VAT", body: "Making Tax Digital ITSA and VAT compliance, scheme selection." },
                { title: "Exit planning", body: "BADR, MBOs, earn-outs, goodwill valuation, due diligence support." },
              ].map((s) => (
                <div key={s.title} className="bg-slate-50 border border-slate-200 p-5">
                  <h3 className="text-base font-bold text-slate-900">{s.title}</h3>
                  <p className="mt-2 text-sm text-slate-600">{s.body}</p>
                </div>
              ))}
            </div>
            <div className="mt-10">
              <Link href="/services" className="inline-flex items-center gap-2 text-orange-600 hover:text-orange-700 font-semibold">
                See all our services <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* LOCAL CASE STUDY */}
      <section className="bg-slate-50 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <p className="text-xs font-bold uppercase tracking-wider text-orange-700 mb-3">
              {city.name} case study (anonymised)
            </p>
            <div className="bg-white border-l-4 border-orange-600 p-6 sm:p-8">
              <Quote className="h-8 w-8 text-orange-300 mb-3" />
              <h3 className="text-xl sm:text-2xl font-bold text-slate-900">
                {city.localCaseStudy.headline}
              </h3>
              <p className="mt-2 text-sm font-mono uppercase tracking-wider text-slate-500">
                {city.localCaseStudy.business_type}
              </p>
              <p className="mt-4 text-base text-slate-700 leading-relaxed">
                {city.localCaseStudy.body}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* LOCAL FAQS */}
      <section className="bg-white py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl mb-8">
              Frequently asked questions from {city.name}
            </h2>
            <dl className="space-y-4">
              {city.localFaqs.map((f) => (
                <div key={f.question} className="border-l-4 border-slate-300 bg-slate-50 p-6">
                  <dt className="text-lg font-bold text-slate-900">{f.question}</dt>
                  <dd className="mt-3 text-base text-slate-700 leading-relaxed">{f.answer}</dd>
                </div>
              ))}
            </dl>

            {/* Adjacent town cross-link (non-templated, one per page) */}
            <div className="mt-12 border-t border-slate-200 pt-8 text-base text-slate-600">
              Also based in or near {city.adjacentTown.name}? See our{" "}
              <Link
                href={`/locations/${city.adjacentTown.slug}`}
                className="text-orange-600 underline hover:text-orange-700 font-semibold"
              >
                accountant in {city.adjacentTown.name}
              </Link>{" "}
              page.
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-700 via-orange-800 to-slate-900" />
        <div className={`${siteContainerLg} relative z-10 py-16 sm:py-20`}>
          <div className="grid gap-8 lg:grid-cols-2 lg:gap-16 items-start">
            <div>
              <h2 className="text-3xl font-bold text-white sm:text-4xl">
                Speak to an accountant in {city.name}
              </h2>
              <p className="mt-4 text-lg text-slate-200 leading-relaxed">
                Book a free 30-minute call. We will talk through your situation and give you clear, practical recommendations. No jargon, no obligation.
              </p>
              <div className="mt-6 space-y-3 text-slate-200">
                <div className="flex items-center gap-3">
                  <Phone className="h-5 w-5 text-orange-300" />
                  <span className="font-semibold">{siteConfig.contact.phone}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-orange-300" />
                  <a href={`mailto:${siteConfig.contact.email}`} className="font-semibold underline">
                    {siteConfig.contact.email}
                  </a>
                </div>
              </div>
              <Link href="/contact" className={`${btnOnOrange} mt-8`}>
                Book a free call
              </Link>
            </div>
            <div className="bg-white p-6 sm:p-8">
              <h3 className="text-xl font-bold text-slate-900 mb-4">Request a callback</h3>
              <LeadForm redirectOnSuccess={false} submitLabel="Book a free call" />
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
