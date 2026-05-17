export type BlogFaq = { question: string; answer: string };

/**
 * Aligns with `09_md_exporter.py` Astro/frontmatter fields plus optional FAQ YAML
 * for on-page rendering (the Python exporter stores FAQs mainly in schema today;
 * add `faqs` in frontmatter when publishing for richer FAQ sections).
 */
export type ImageCredit = {
  photographer?: string;
  photographerUrl?: string;
  sourceUrl?: string;
  source?: string;
};

export type BlogFrontmatter = {
  title: string;
  slug: string;
  date: string;
  /** Date the post was last meaningfully edited. Falls back to `date`. */
  updatedDate?: string;
  /**
   * Free-text author name from frontmatter. Used as the byline label when
   * `authorSlug` doesn't resolve to a /team/[slug] entry. Legacy posts use
   * this; new posts should set `authorSlug` instead.
   */
  author: string;
  /** Slug into /team/[slug] for the canonical Person schema author. */
  authorSlug?: string;
  category: string;
  metaTitle: string;
  metaDescription: string;
  altText?: string;
  image?: string;
  imageCredit?: ImageCredit;
  h1: string;
  summary: string;
  /**
   * Optional structured 3–5 bullet "Key takeaways" for AI extraction and
   * voice-assistant retrieval. Falls back to `summary` if absent.
   */
  keyTakeaways?: string[];
  /** Raw JSON-LD string from `05_schema_builder.py` when present */
  schema?: string;
  canonical?: string;
  faqs?: BlogFaq[];
};

export type BlogPost = BlogFrontmatter & {
  contentHtml: string;
};
