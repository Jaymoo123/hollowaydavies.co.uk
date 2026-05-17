import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { MapPin, ArrowRight } from "lucide-react";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { CITIES } from "./[slug]/data";

export const metadata: Metadata = {
  title: `Accountants near you across the UK | ${siteConfig.name}`,
  description:
    "ICAEW chartered accountants for UK businesses across nearly 200 UK cities and towns. Local context, sector emphasis, fixed fees. Find your accountant in London, Manchester, Birmingham, Leeds, Bristol, Edinburgh and many more.",
  alternates: { canonical: `${siteConfig.url}/locations` },
  openGraph: {
    title: `Accountants near you across the UK | ${siteConfig.name}`,
    description: "ICAEW chartered accountants for UK businesses across nearly 200 cities and towns.",
    url: `${siteConfig.url}/locations`,
    type: "website",
  },
};

// Tiered city groupings reflect business density, not arbitrary order.
const METRO_SLUGS = [
  "london", "manchester", "birmingham", "leeds", "bristol",
  "edinburgh", "glasgow", "liverpool", "sheffield", "newcastle",
];
const REGIONAL_SLUGS = [
  "bradford", "nottingham", "cardiff", "reading", "brighton",
  "portsmouth", "coventry", "bournemouth", "plymouth", "hull",
  "leicester", "stoke-on-trent", "wolverhampton", "derby", "southampton",
  "milton-keynes", "northampton", "oxford", "cambridge", "york",
];

function CityCard({ slug }: { slug: string }) {
  const city = CITIES[slug];
  if (!city) return null;
  const hero = (city as unknown as { heroImage?: { url: string; alt: string } }).heroImage;
  return (
    <Link
      href={`/locations/${city.slug}`}
      className="group block bg-white border border-slate-200 hover:border-orange-600 hover:shadow-md transition-all overflow-hidden"
    >
      {hero ? (
        <div className="relative h-44 w-full overflow-hidden bg-slate-100">
          <Image
            src={hero.url}
            alt={hero.alt}
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            className="object-cover group-hover:scale-105 transition-transform duration-500"
          />
        </div>
      ) : (
        <div className="relative h-44 w-full bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center">
          <MapPin className="h-12 w-12 text-white opacity-50" />
        </div>
      )}
      <div className="p-5 sm:p-6">
        <h3 className="text-xl font-bold text-slate-900 group-hover:text-orange-700 transition-colors">
          Accountant in {city.name}
        </h3>
        <p className="mt-2 text-sm text-slate-500 font-mono uppercase tracking-wider">
          {city.region}
        </p>
        <p className="mt-3 text-sm text-slate-600 leading-relaxed line-clamp-3">
          {city.businessHubs.slice(0, 3).join(" · ")}
        </p>
        <div className="mt-4 flex items-center text-orange-600 font-semibold text-sm">
          View {city.name} page
          <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
  );
}

function SimpleCityLink({ slug }: { slug: string }) {
  const city = CITIES[slug];
  if (!city) return null;
  return (
    <Link
      href={`/locations/${city.slug}`}
      className="group flex items-center justify-between gap-2 border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
    >
      <span className="truncate font-medium">{city.name}</span>
      <ArrowRight className="h-3 w-3 shrink-0 group-hover:translate-x-0.5 transition-transform" />
    </Link>
  );
}

function CityCardGroup({ heading, slugs }: { heading: string; slugs: string[] }) {
  const available = slugs.filter((s) => CITIES[s]);
  if (available.length === 0) return null;
  return (
    <div className="mb-14">
      <h2 className="text-2xl font-bold text-slate-900 mb-6 pb-3 border-b border-slate-200">
        {heading}
      </h2>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {available.map((s) => (
          <CityCard key={s} slug={s} />
        ))}
      </div>
    </div>
  );
}

function CityLinkGroup({ heading, slugs }: { heading: string; slugs: string[] }) {
  const available = slugs.filter((s) => CITIES[s]).sort((a, b) =>
    (CITIES[a]?.name || "").localeCompare(CITIES[b]?.name || "")
  );
  if (available.length === 0) return null;
  return (
    <div className="mb-14 last:mb-0">
      <h2 className="text-2xl font-bold text-slate-900 mb-6 pb-3 border-b border-slate-200">
        {heading}
      </h2>
      <p className="mb-4 text-sm text-slate-600">
        {available.length} location pages, each with local sector context, named employers and a town-specific FAQ.
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
        {available.map((s) => (
          <SimpleCityLink key={s} slug={s} />
        ))}
      </div>
    </div>
  );
}

export default function LocationsIndexPage() {
  const totalCities = Object.keys(CITIES).length;
  const featuredSet = new Set([...METRO_SLUGS, ...REGIONAL_SLUGS]);
  const restSlugs = Object.keys(CITIES).filter((s) => !featuredSet.has(s));
  return (
    <>
      <section className="bg-slate-900 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <Breadcrumb
            variant="light"
            items={[
              { label: "Home", href: "/" },
              { label: "Locations" },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-orange-600 px-3 py-1.5 text-xs font-bold text-white uppercase tracking-wider mb-4">
              <MapPin className="h-3.5 w-3.5" />
              UK coverage
            </div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              Find an accountant in your part of the UK
            </h1>
            <p className="mt-4 text-lg text-slate-300 leading-relaxed">
              ICAEW chartered accountants for limited companies, contractors, sole traders, partnerships and small businesses across {totalCities} UK cities and towns. Every location page is researched against the local economic mix, named employers and sector emphasis. National coverage, remote-first, in-person on request.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-slate-50 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto">
            <CityCardGroup heading="Major cities" slugs={METRO_SLUGS} />
            <CityCardGroup heading="Regional cities" slugs={REGIONAL_SLUGS} />
            <CityLinkGroup heading="More UK locations" slugs={restSlugs} />
          </div>
        </div>
      </section>
    </>
  );
}
