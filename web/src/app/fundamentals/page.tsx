import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { siteConfig } from "@/config/site";
import { getAllFundamentals } from "@/lib/fundamentals";
import { ArrowRight } from "lucide-react";

export const metadata: Metadata = {
  title: "Fundamentals | Pillar Guides for UK Business Owners",
  description:
    "Definitive pillar guides on UK business tax, finance, incorporation, IR35, MTD, R&D, exit planning and more. Written by ICAEW qualified accountants for limited companies, contractors, sole traders and partnerships.",
  alternates: { canonical: `${siteConfig.url}/fundamentals` },
  openGraph: {
    title: "Fundamentals | Pillar Guides for UK Business Owners",
    description:
      "Definitive pillar guides on UK business tax, finance, incorporation, IR35, MTD, R&D, exit planning and more.",
    url: `${siteConfig.url}/fundamentals`,
    type: "website",
  },
};

export default function FundamentalsIndexPage() {
  const guides = getAllFundamentals();

  return (
    <>
      <section className="relative h-[350px] overflow-hidden">
        <Image
          src="https://images.unsplash.com/photo-1453928582365-b6ad33cbcf64?w=2000&q=85"
          alt="Open book with reading glasses on a desk"
          fill
          priority
          sizes="100vw"
          className="object-cover brightness-60"
        />
        <div className="absolute inset-0 bg-slate-900/85" />
        <div className={`${siteContainerLg} relative z-10 h-full flex items-center`}>
          <div className="max-w-3xl">
            <Breadcrumb
              variant="light"
              items={[
                { label: "Home", href: "/" },
                { label: "Guides", href: "/fundamentals" },
                { label: "Fundamentals" },
              ]}
            />
            <h1 className="mt-6 text-4xl font-bold text-white sm:text-5xl lg:text-6xl">
              UK business finance fundamentals
            </h1>
            <p className="mt-4 text-xl text-slate-200">
              The definitive pillar guides we wish every UK business owner had read before incorporating, hiring, or selling.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-slate-50 py-16 sm:py-20">
        <div className={siteContainerLg}>
          <div className="max-w-6xl mx-auto">
            {guides.length === 0 ? (
              <p className="text-base text-slate-600">No pillar guides published yet. Check back soon.</p>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {guides.map((g) => (
                  <Link
                    key={g.slug}
                    href={`/fundamentals/${g.slug}`}
                    className="group block bg-white border border-slate-200 p-6 shadow-sm hover:shadow-md hover:border-orange-600 transition-all"
                  >
                    <p className="text-xs font-bold uppercase tracking-wider text-orange-700">
                      {g.category}
                    </p>
                    <h2 className="mt-3 text-xl font-semibold text-slate-900 group-hover:text-orange-600 transition-colors">
                      {g.title}
                    </h2>
                    <p className="mt-3 text-sm text-slate-600 leading-relaxed">{g.summary}</p>
                    <div className="mt-4 flex items-center text-orange-600 font-medium text-sm">
                      Read the guide
                      <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
