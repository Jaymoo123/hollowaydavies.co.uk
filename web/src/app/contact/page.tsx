import type { Metadata } from "next";
import { LeadForm } from "@/components/forms/LeadForm";
import { siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { JsonLd, referencedOrganization } from "@/lib/schema";

export const metadata: Metadata = {
  title: `Contact`,
  description: `Speak to an ICAEW chartered accountant about your UK business. Same-day response, fixed fees, no obligation.`,
  alternates: { canonical: `${siteConfig.url}/contact` },
  openGraph: {
    title: `Contact | ${siteConfig.name}`,
    description: "Speak to an ICAEW chartered accountant. Same-day response, fixed fees, no obligation.",
    url: `${siteConfig.url}/contact`,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: `Contact | ${siteConfig.name}`,
    description: "Speak to an ICAEW chartered accountant. Same-day response, fixed fees, no obligation.",
  },
};

export default function ContactPage() {
  const contactPage = {
    "@context": "https://schema.org",
    "@type": "ContactPage" as const,
    "@id": `${siteConfig.url}/contact#page`,
    name: `Contact ${siteConfig.name}`,
    url: `${siteConfig.url}/contact`,
    description: "Contact form and direct line for new enquiries.",
    inLanguage: "en-GB",
    about: referencedOrganization(),
    mainEntity: {
      "@type": "Organization",
      "@id": `${siteConfig.url}#organization`,
      name: siteConfig.name,
      email: siteConfig.contact.email,
      telephone: siteConfig.contact.phone,
      url: siteConfig.url,
      contactPoint: {
        "@type": "ContactPoint",
        contactType: "customer service",
        email: siteConfig.contact.email,
        telephone: siteConfig.contact.phone,
        areaServed: "GB",
        availableLanguage: "en",
      },
    },
  };

  return (
    <>
      <JsonLd data={contactPage} />

      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <div className="grid lg:grid-cols-[1fr_1.2fr] gap-12 lg:gap-20">
            <div>
              <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
                Talk to an accountant
              </p>
              <h1 className="mt-4 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl lg:text-6xl text-balance">
                Start with a short call.
              </h1>
              <p className="mt-6 max-w-prose text-lg leading-relaxed text-neutral-600">
                Tell us where the business sits today, what is and isn&rsquo;t working, and we&rsquo;ll come
                back with a short note on what the engagement would look like and what it would
                cost. No pitch, no follow-up sequence.
              </p>

              <div className="mt-12">
                <p className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-4">
                  What happens next
                </p>
                <ul className="space-y-4 max-w-md">
                  {[
                    "Reply within one working day, usually same day.",
                    "A short call to understand your situation and what you need.",
                    "Plain-English recommendations, with or without us.",
                    "Fixed-fee quote in writing if we&rsquo;re a fit.",
                  ].map((line, i) => (
                    <li key={i} className="grid grid-cols-[2rem_1fr] gap-3 items-start">
                      <span className="font-mono text-sm text-orange-500">{String(i + 1).padStart(2, "0")}</span>
                      <span className="text-base leading-relaxed text-neutral-700" dangerouslySetInnerHTML={{ __html: line }} />
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-12 border-t border-neutral-200 pt-8 max-w-md">
                <p className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-4">
                  Or directly
                </p>
                <dl className="space-y-3 text-sm">
                  <div className="grid grid-cols-[5rem_1fr] gap-2">
                    <dt className="text-neutral-500">Email</dt>
                    <dd>
                      <a href={`mailto:${siteConfig.contact.email}`} className="text-neutral-900 hover:text-orange-600 underline underline-offset-4">
                        {siteConfig.contact.email}
                      </a>
                    </dd>
                  </div>
                  <div className="grid grid-cols-[5rem_1fr] gap-2">
                    <dt className="text-neutral-500">Phone</dt>
                    <dd>
                      <a href={`tel:${siteConfig.contact.phone.replace(/\s/g, "")}`} className="text-neutral-900 hover:text-orange-600 underline underline-offset-4">
                        {siteConfig.contact.phone}
                      </a>
                    </dd>
                  </div>
                </dl>
              </div>
            </div>

            <div>
              <div className="border border-neutral-200 bg-white p-8 lg:p-10">
                <h2 className="text-xl font-semibold tracking-tight text-neutral-900">Send an enquiry</h2>
                <p className="mt-2 text-sm text-neutral-600">
                  Takes about a minute. We don&rsquo;t share your details.
                </p>
                <div className="mt-8">
                  <LeadForm redirectOnSuccess submitLabel="Send enquiry" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
