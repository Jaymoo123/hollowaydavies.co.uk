/**
 * Composable JSON-LD schema builders for Holloway Davies.
 *
 * Each builder returns a typed plain object that can be:
 *   - serialised inline via `serialize()` for `dangerouslySetInnerHTML`
 *   - rendered via the `<JsonLd data={...} />` component
 *   - composed into arrays (multi-type pages: Article + FAQPage + Breadcrumb)
 *
 * Pattern:
 *
 *   import { JsonLd, buildBlogPosting, buildBreadcrumb, buildFaqPage } from "@/lib/schema";
 *
 *   const data = [
 *     buildBreadcrumb(crumbs),
 *     buildBlogPosting(post, path),
 *     ...(post.faqs ? [buildFaqPage(post.faqs)!] : []),
 *   ];
 *
 *   return <JsonLd data={data} />;
 */

export * from "./types";
export * from "./serialize";
export * from "./og";
export { JsonLd } from "./JsonLd";

export * from "./organization";
export * from "./person";
export * from "./breadcrumb";
export * from "./blog-posting";
export * from "./article";
export * from "./faq-page";
export * from "./service";
export * from "./local-business";
export * from "./defined-term";
export * from "./web-application";
export * from "./dataset";
export * from "./course";
export * from "./howto";
export * from "./collection-page";
