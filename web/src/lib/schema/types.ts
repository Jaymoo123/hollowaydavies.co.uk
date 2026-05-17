/**
 * Shared JSON-LD types. Loose by design, schema.org accepts a lot of shapes
 * and we don't want to fight the type system. Builders return `SchemaThing`
 * objects that can be composed and serialised.
 */

export type SchemaThing = {
  "@context"?: string | string[];
  "@type": string | string[];
  "@id"?: string;
  [key: string]: unknown;
};

export type Organization = SchemaThing & {
  "@type": "Organization" | "ProfessionalService" | "AccountingService" | "LocalBusiness";
  name: string;
  url: string;
  logo?: { "@type": "ImageObject"; url: string };
  sameAs?: string[];
  areaServed?: SchemaThing | SchemaThing[] | string | string[];
};

export type Person = SchemaThing & {
  "@type": "Person";
  name: string;
  url?: string;
  jobTitle?: string;
  knowsAbout?: string[];
  worksFor?: SchemaThing;
  sameAs?: string[];
};

export type ImageObject = {
  "@type": "ImageObject";
  url: string;
  width?: number;
  height?: number;
  caption?: string;
};

export type PostalAddress = {
  "@type": "PostalAddress";
  streetAddress?: string;
  addressLocality?: string;
  addressRegion?: string;
  postalCode?: string;
  addressCountry?: string;
};
