import type { Metadata } from "next";
import Link from "next/link";
import { MapPin, ArrowRight, BadgeCheck, Phone, Mail } from "lucide-react";
import { siteContainerLg, btnPrimary } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { LeadForm } from "@/components/forms/LeadForm";
import { CITIES } from "../locations/[slug]/data";

const pageUrl = `${siteConfig.url}/accountant-near-me`;

export const metadata: Metadata = {
  title: `Accountant near me | ${siteConfig.name}`,
  description:
    "ICAEW chartered accountants serving UK businesses in every major town and city. Find an accountant near you across 190+ UK locations. Remote-first, fixed fees, in-person on request.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: `Accountant near me | ${siteConfig.name}`,
    description: "ICAEW chartered accountants serving UK businesses in every major town and city.",
    url: pageUrl,
    type: "website",
  },
};

export default function AccountantNearMePage() {
  const allCities = Object.values(CITIES).sort((a, b) => a.name.localeCompare(b.name));
  return (
    <>
      {/* Hero */}
      <section className="bg-slate-900 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[{ label: "Home", href: "/" }, { label: "Accountant near me" }]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <MapPin className="h-3.5 w-3.5" />
              UK-wide coverage
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Looking for an accountant near you?
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              {siteConfig.name} is an ICAEW chartered accountancy firm serving UK limited companies, contractors, sole traders, partnerships and small businesses in every major town and city. We work remote-first, with in-person meetings available on request. {allCities.length} dedicated location pages, one for each town and city we serve.
            </p>
            <div className="mt-6 flex flex-wrap gap-4 text-sm text-slate-300">
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
                <span className="font-semibold">{allCities.length} UK locations</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How remote-first works */}
      <section className="bg-white py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl">How does a remote-first accountant work?</h2>
            <p className="mt-4 text-base sm:text-lg text-slate-700 leading-relaxed">
              You probably don't actually need an accountant physically next door. You need someone who returns your calls, files your accounts on time, and tells you what to do about MTD, R&amp;D, dividends or your next hire. We do all that over phone and video, with in-person meetings on request in the major UK cities. Every invoice, return and discussion lives in a shared cloud workspace (Xero, FreeAgent, QuickBooks, whichever you use). You see the same numbers we see, in real time, from anywhere.
            </p>
            <p className="mt-4 text-base sm:text-lg text-slate-700 leading-relaxed">
              For most UK limited companies, contractors and sole traders, remote-first is the better service model: lower fees because we are not paying for a high-street office, faster response because we are not booking meeting rooms, and the same ICAEW-qualified accountant on your account year after year.
            </p>
          </div>
        </div>
      </section>

      {/* Alphabetical city grid */}
      <section className="bg-slate-50 py-16">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-bold text-slate-900 sm:text-3xl mb-2">Find your nearest location page</h2>
            <p className="text-base text-slate-600 mb-8">
              Each page covers local sectors, named employers, an anonymised case study, and frequently asked questions for that town.
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
              {allCities.map((c) => (
                <Link
                  key={c.slug}
                  href={`/locations/${c.slug}`}
                  className="group flex items-center justify-between gap-2 border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
                >
                  <span className="truncate font-medium">{c.name}</span>
                  <ArrowRight className="h-3 w-3 shrink-0 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              ))}
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
                Don't see your town?
              </h2>
              <p className="mt-4 text-lg text-slate-200 leading-relaxed">
                We serve UK businesses nationwide, not just the {allCities.length} cities listed. Book a free 30-minute call and we'll explain how the remote-first service works for your situation. No jargon, no obligation.
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
              <Link href="/contact" className={`${btnPrimary} mt-8`}>
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
