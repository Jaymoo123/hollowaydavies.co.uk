/**
 * Backwards-compatibility shim. The previous monolithic `lib/schema.ts`
 * has been split into a folder of composable builders at `lib/schema/`.
 *
 * Existing callers that import named functions from `@/lib/schema` keep
 * working unchanged via this re-export. New code should import the
 * granular builders directly:
 *
 *   import { buildBlogPosting, buildFaqPage, JsonLd } from "@/lib/schema";
 */

import type { BlogPost } from "@/types/blog";
import type { BreadcrumbItem } from "@/components/ui/Breadcrumb";

import { serialize } from "./schema/serialize";
import { buildBreadcrumb } from "./schema/breadcrumb";
import { buildBlogPosting } from "./schema/blog-posting";
import { buildArticle } from "./schema/article";
import { buildFaqPage } from "./schema/faq-page";

export * from "./schema/index";

/** Legacy: returns serialised JSON-LD string for direct dangerouslySetInnerHTML usage. */
export function buildBreadcrumbJsonLd(items: BreadcrumbItem[]): string {
  return serialize(buildBreadcrumb(items));
}

/** Legacy: returns serialised JSON-LD string for BlogPosting + optional FAQPage. */
export function buildBlogPostingJsonLd(post: BlogPost, path: string): string {
  const article = buildBlogPosting(post, path);
  const faq = post.faqs && post.faqs.length ? buildFaqPage(post.faqs) : null;
  return serialize(faq ? [article, faq] : article);
}

/** Legacy: returns serialised JSON-LD string for Article + optional FAQPage. */
export function buildArticleJsonLd(post: BlogPost, path: string): string {
  const article = buildArticle(post, path);
  const faq = post.faqs && post.faqs.length ? buildFaqPage(post.faqs) : null;
  return serialize(faq ? [article, faq] : article);
}
