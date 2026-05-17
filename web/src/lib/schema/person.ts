import { siteConfig } from "@/config/site";
import { getTeamMember } from "@/app/team/[slug]/data";
import type { Person, SchemaThing } from "./types";

/**
 * Person schema for a /team/[slug] member. Used as `author` on blog and
 * article pages so AI engines and Google have a real Person URL to crawl
 * for E-E-A-T signals.
 */
export function buildPerson(slug: string): Person | null {
  const member = getTeamMember(slug);
  if (!member) return null;
  const url = `${siteConfig.url}/team/${member.slug}`;
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    "@id": `${url}#person`,
    name: member.name,
    jobTitle: member.role,
    url,
    description: member.shortBio,
    knowsAbout: member.expertise,
    worksFor: {
      "@type": "Organization",
      "@id": `${siteConfig.url}#organization`,
      name: siteConfig.name,
      url: siteConfig.url,
    },
    ...(member.links && member.links.length
      ? { sameAs: member.links.map((l) => l.url) }
      : {}),
  };
}

/**
 * Person reference (just @id + name + url) for use as `author` inside
 * another schema. Falls back to a free-text Person when the slug doesn't
 * resolve.
 */
export function referencedPerson(slug: string | undefined, fallbackName?: string): SchemaThing {
  const member = slug ? getTeamMember(slug) : null;
  if (member) {
    const url = `${siteConfig.url}/team/${member.slug}`;
    return {
      "@type": "Person",
      "@id": `${url}#person`,
      name: member.name,
      url,
    };
  }
  return {
    "@type": "Person",
    name: fallbackName || `${siteConfig.name} Editorial Team`,
    url: `${siteConfig.url}/about`,
  };
}
