import { siteConfig } from "@/config/site";
import type { SchemaThing } from "./types";

export type CollectionPageInput = {
  name: string;
  description: string;
  /** Path of the page (without origin), e.g. "/blog/tax-and-compliance" */
  path: string;
  /** Optional language override */
  inLanguage?: string;
};

/**
 * CollectionPage for blog category indexes, glossary index, calculator
 * index, agency-type index, pages that group/list other pages.
 */
export function buildCollectionPage(input: CollectionPageInput): SchemaThing {
  const url = `${siteConfig.url}${input.path}`;
  return {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "@id": `${url}#page`,
    name: input.name,
    description: input.description,
    url,
    inLanguage: input.inLanguage || "en-GB",
    isPartOf: {
      "@type": "WebSite",
      "@id": `${siteConfig.url}#website`,
      url: siteConfig.url,
      name: siteConfig.name,
    },
  };
}
