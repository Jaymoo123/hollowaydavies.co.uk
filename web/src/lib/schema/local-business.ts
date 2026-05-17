import { siteConfig } from "@/config/site";
import type { Organization, PostalAddress, SchemaThing } from "./types";

export type LocalBusinessInput = {
  /** City / location name (used in title + areaServed) */
  city: string;
  /** Canonical URL, absolute or path-only */
  url: string;
  /** Plain-English page title, used as `name` */
  name: string;
  description: string;
  /** Optional street address; LocalBusiness needs at least addressLocality + addressCountry */
  address?: Partial<PostalAddress>;
  /** Geo coordinates if known */
  geo?: { latitude: number; longitude: number };
  /** Sub-area cities served from this location */
  areaServed?: string[];
  /** Opening hours specifications */
  openingHours?: string[];
};

/**
 * AccountingService (a LocalBusiness sub-type) for UK city pages. The
 * stricter sub-type signals to Google that this is a regulated accountant
 * presence in that city.
 */
export function buildAccountingService(input: LocalBusinessInput): Organization {
  const url = input.url.startsWith("http") ? input.url : `${siteConfig.url}${input.url}`;

  const address: PostalAddress = {
    "@type": "PostalAddress",
    addressLocality: input.address?.addressLocality || input.city,
    addressCountry: input.address?.addressCountry || "GB",
    ...(input.address?.streetAddress ? { streetAddress: input.address.streetAddress } : {}),
    ...(input.address?.addressRegion ? { addressRegion: input.address.addressRegion } : {}),
    ...(input.address?.postalCode ? { postalCode: input.address.postalCode } : {}),
  };

  const out: Organization = {
    "@context": "https://schema.org",
    "@type": "AccountingService",
    "@id": `${url}#localbusiness`,
    name: input.name,
    description: input.description,
    url,
    image: `${siteConfig.url}${siteConfig.publisherLogoUrl}`,
    logo: {
      "@type": "ImageObject",
      url: `${siteConfig.url}${siteConfig.publisherLogoUrl}`,
    },
    email: siteConfig.contact.email,
    telephone: siteConfig.contact.phone,
    address,
    areaServed: (input.areaServed || [input.city]).map((c) => ({
      "@type": "City",
      name: c,
    })),
  };

  if (input.geo) {
    (out as Record<string, unknown>).geo = {
      "@type": "GeoCoordinates",
      latitude: input.geo.latitude,
      longitude: input.geo.longitude,
    };
  }

  if (input.openingHours && input.openingHours.length) {
    (out as Record<string, unknown>).openingHoursSpecification = input.openingHours;
  }

  return out;
}

/**
 * Convenience: emit a Service + LocalBusiness pair for a city page where
 * the LocalBusiness is the "where" and the Service is the "what". Most
 * city pages will use this together with the Breadcrumb.
 */
export function buildCityPage(input: LocalBusinessInput & { serviceName: string }): SchemaThing[] {
  return [buildAccountingService(input)];
}
