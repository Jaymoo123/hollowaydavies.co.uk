import { siteConfig } from "@/config/site";
import { referencedOrganization } from "./organization";
import type { SchemaThing } from "./types";

export type ServiceInput = {
  name: string;
  description: string;
  /** Canonical URL of the service page, absolute or path-only */
  url: string;
  /** e.g. "Tax planning", "Bookkeeping", "R&D tax credits". Free-text. */
  serviceType?: string;
  /** "United Kingdom" or list of cities */
  areaServed?: string | string[];
  /** Optional list of inclusions / sub-services */
  hasOfferCatalog?: { name: string; items: string[] };
  /** Audience the service is built for */
  audience?: string;
};

/**
 * Service schema for commercial pages (e.g. /services/accounting-for-agencies,
 * /agencies/marketing-agencies, /r-and-d-credits). Always associates with
 * the canonical Organization as `provider`.
 */
export function buildService(input: ServiceInput): SchemaThing {
  const url = input.url.startsWith("http") ? input.url : `${siteConfig.url}${input.url}`;

  const out: SchemaThing = {
    "@context": "https://schema.org",
    "@type": "Service",
    "@id": `${url}#service`,
    name: input.name,
    description: input.description,
    url,
    provider: referencedOrganization(),
    ...(input.serviceType ? { serviceType: input.serviceType } : {}),
    ...(input.audience
      ? {
          audience: {
            "@type": "Audience",
            audienceType: input.audience,
          },
        }
      : {}),
  };

  if (input.areaServed) {
    const areas = Array.isArray(input.areaServed) ? input.areaServed : [input.areaServed];
    out.areaServed = areas.map((a) =>
      a === "United Kingdom" || a === "UK"
        ? { "@type": "Country", name: "United Kingdom" }
        : { "@type": "City", name: a },
    );
  }

  if (input.hasOfferCatalog) {
    out.hasOfferCatalog = {
      "@type": "OfferCatalog",
      name: input.hasOfferCatalog.name,
      itemListElement: input.hasOfferCatalog.items.map((label, i) => ({
        "@type": "Offer",
        position: i + 1,
        itemOffered: {
          "@type": "Service",
          name: label,
        },
      })),
    };
  }

  return out;
}
