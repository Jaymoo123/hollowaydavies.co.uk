import { siteConfig } from "@/config/site";
import type { SchemaThing } from "./types";

export type DefinedTermInput = {
  /** Slug of the term, used in the @id */
  slug: string;
  /** The term being defined */
  term: string;
  /** Short definition (1-3 sentences) */
  definition: string;
  /** Optional subject classification, e.g. "UK tax", "Accounting" */
  inDefinedTermSet?: string;
};

/**
 * DefinedTerm schema for individual glossary entries.
 */
export function buildDefinedTerm(input: DefinedTermInput): SchemaThing {
  const url = `${siteConfig.url}/glossary/${input.slug}`;
  const setUrl = `${siteConfig.url}/glossary`;
  return {
    "@context": "https://schema.org",
    "@type": "DefinedTerm",
    "@id": `${url}#term`,
    name: input.term,
    description: input.definition,
    url,
    inDefinedTermSet: input.inDefinedTermSet || setUrl,
  };
}

/**
 * DefinedTermSet for the glossary index page. Lists all terms by name + URL.
 */
export function buildDefinedTermSet(
  terms: { slug: string; term: string }[],
): SchemaThing {
  const url = `${siteConfig.url}/glossary`;
  return {
    "@context": "https://schema.org",
    "@type": "DefinedTermSet",
    "@id": `${url}#termset`,
    name: "Holloway Davies Glossary",
    description:
      "Plain-English definitions of UK business tax, finance, and accounting terms.",
    url,
    inLanguage: "en-GB",
    hasDefinedTerm: terms.map((t) => ({
      "@type": "DefinedTerm",
      name: t.term,
      url: `${siteConfig.url}/glossary/${t.slug}`,
    })),
  };
}
