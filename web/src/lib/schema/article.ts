import { siteConfig } from "@/config/site";
import type { BlogPost } from "@/types/blog";
import { referencedOrganization } from "./organization";
import { referencedPerson } from "./person";
import { buildOgImageUrl } from "./og";
import type { SchemaThing } from "./types";

const SPEAKABLE = {
  "@type": "SpeakableSpecification" as const,
  cssSelector: [".tldr", "h1"],
};

/**
 * Article schema for Fundamentals pillar guides and founder stories, more
 * authoritative than BlogPosting and signals long-form / evergreen content
 * to crawlers.
 */
export function buildArticle(post: BlogPost, path: string): SchemaThing {
  const url = `${siteConfig.url}${path}`;
  const imageUrl = post.image
    ? post.image.startsWith("http")
      ? post.image
      : `${siteConfig.url}${post.image}`
    : buildOgImageUrl(post.h1, post.category);

  return {
    "@context": "https://schema.org",
    "@type": "Article",
    "@id": `${url}#article`,
    headline: post.h1,
    description: post.metaDescription,
    image: imageUrl,
    datePublished: post.date,
    dateModified: post.updatedDate || post.date,
    author: referencedPerson(post.authorSlug || "emma-carter", post.author),
    publisher: referencedOrganization(),
    mainEntityOfPage: { "@type": "WebPage", "@id": url },
    articleSection: post.category,
    inLanguage: "en-GB",
    speakable: SPEAKABLE,
    isAccessibleForFree: true,
  };
}
