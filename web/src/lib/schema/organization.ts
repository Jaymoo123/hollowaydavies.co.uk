import { siteConfig } from "@/config/site";
import { niche } from "@/config/niche-loader";
import type { Organization, SchemaThing } from "./types";

const ORG_ID = `${siteConfig.url}#organization`;

/**
 * Canonical Organization schema. Use as the top-level Organization on the
 * homepage; reference downstream pages with `referencedOrganization()` so
 * JSON-LD parsers de-duplicate to the single full record.
 */
export function buildOrganization(): Organization {
  return {
    "@context": "https://schema.org",
    "@type": (niche.seo.organization_type as Organization["@type"]) || "ProfessionalService",
    "@id": ORG_ID,
    name: siteConfig.legalName,
    alternateName: siteConfig.name,
    url: siteConfig.url,
    description: siteConfig.description,
    logo: {
      "@type": "ImageObject",
      url: `${siteConfig.url}${siteConfig.publisherLogoUrl}`,
    },
    image: `${siteConfig.url}${siteConfig.publisherLogoUrl}`,
    email: siteConfig.contact.email,
    telephone: siteConfig.contact.phone,
    areaServed: niche.seo.service_areas.map((s) => ({
      "@type": "City",
      name: s,
    })),
    knowsAbout: [
      "UK corporation tax",
      "Marginal relief and the small profits rate",
      "Director salary and dividend optimisation",
      "VAT registration and scheme selection",
      "Making Tax Digital for VAT and ITSA",
      "PAYE and employer National Insurance",
      "R&D tax credits for UK SMEs",
      "Incorporation timing and structure",
      "Business Asset Disposal Relief and exit planning",
      "Self-assessment for sole traders and partnerships",
      "Bookkeeping for UK small businesses",
    ],
    slogan: siteConfig.tagline,
  };
}

/**
 * Lightweight reference to the canonical Organization, used as `publisher`
 * or `provider` on downstream schema objects so JSON-LD parsers can
 * de-duplicate to the single full record.
 */
export function referencedOrganization(): SchemaThing {
  return {
    "@type": "Organization",
    "@id": ORG_ID,
    name: siteConfig.name,
    url: siteConfig.url,
    logo: {
      "@type": "ImageObject",
      url: `${siteConfig.url}${siteConfig.publisherLogoUrl}`,
    },
  };
}

/**
 * WebSite schema for the homepage. Includes a SearchAction so Google can
 * render the sitelinks search box.
 */
export function buildWebSite(): SchemaThing {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": `${siteConfig.url}#website`,
    url: siteConfig.url,
    name: siteConfig.name,
    description: siteConfig.description,
    inLanguage: "en-GB",
    publisher: { "@id": ORG_ID },
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: `${siteConfig.url}/blog?q={search_term_string}`,
      },
      "query-input": "required name=search_term_string",
    },
  };
}
