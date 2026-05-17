import Link from "next/link";
import Image from "next/image";
import type { BlogPost } from "@/types/blog";
import { buildBlogPostingJsonLd } from "@/lib/schema";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { niche } from "@/config/niche-loader";
import { TableOfContents } from "@/components/blog/TableOfContents";
import { ReadingProgress } from "@/components/blog/ReadingProgress";
import { AuthorByline } from "@/components/blog/AuthorByline";
import { extractHeadings } from "@/lib/markdown-utils";
import { calculateReadTime } from "@/lib/blog";
import { InlinePrompt } from "@/components/newsletter/InlinePrompt";
import { LeadForm } from "@/components/forms/LeadForm";

type BlogPostRendererProps = {
  post: BlogPost;
  categorySlug: string;
  related?: { slug: string; title: string; summary: string; categorySlug: string }[];
};

function formatUkDate(isoDate: string): string {
  const d = new Date(isoDate);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}

export function BlogPostRenderer({ post, categorySlug, related = [] }: BlogPostRendererProps) {
  const headings = extractHeadings(post.contentHtml);
  const readTime = calculateReadTime(post.contentHtml);
  const jsonLd =
    post.schema?.trim() ||
    buildBlogPostingJsonLd(post, `/blog/${categorySlug}/${post.slug}`);

  // Resolve the byline: prefer the new authorSlug field; default every post to
  // the editorial lead so the Person schema in JSON-LD always has a real
  // /team/[slug] URL. Legacy free-text `author` is honoured as a label
  // fallback only when no slug resolves.
  const authorSlug = post.authorSlug || "emma-carter";

  const takeaways = post.keyTakeaways && post.keyTakeaways.length > 0
    ? post.keyTakeaways
    : null;

  return (
    <>
      <ReadingProgress />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: jsonLd }}
      />

      <section className="relative h-[420px] sm:h-[480px] lg:h-[520px] overflow-hidden">
        {post.image ? (
          <Image
            src={post.image}
            alt={post.altText || post.title}
            fill
            priority
            sizes="100vw"
            className="object-cover scale-110 blur-sm"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-orange-700 via-orange-800 to-slate-900" />
        )}
        <div className="absolute inset-0 bg-slate-900/70" />
        <div className={`${siteContainerLg} relative z-10 h-full flex items-end pb-10 sm:pb-14`}>
          <div className="max-w-4xl">
            <Breadcrumb
              variant="light"
              items={[
                { label: "Home", href: "/" },
                { label: "Blog", href: "/blog" },
                { label: post.category, href: `/blog/${categorySlug}` },
                { label: post.title },
              ]}
            />
            <p className="mt-6 text-xs font-bold uppercase tracking-wider text-orange-300">
              {post.category}
            </p>
            <h1 className="mt-3 text-3xl font-bold leading-tight text-white sm:text-4xl md:text-5xl">
              {post.h1}
            </h1>
            <p className="mt-4 text-sm text-slate-300">
              {readTime > 0 && <span>{readTime} min read</span>}
              {post.date && (
                <>
                  {readTime > 0 ? " · " : null}
                  <time dateTime={post.date}>Published {formatUkDate(post.date)}</time>
                </>
              )}
              {post.updatedDate && post.updatedDate !== post.date && (
                <>
                  {" · "}
                  <time dateTime={post.updatedDate}>
                    Updated {formatUkDate(post.updatedDate)}
                  </time>
                </>
              )}
            </p>
          </div>
        </div>
        {post.imageCredit?.photographer ? (
          <p className="absolute bottom-2 right-3 z-10 text-[10px] text-slate-400/80">
            Photo:{" "}
            {post.imageCredit.photographerUrl ? (
              <a
                href={post.imageCredit.photographerUrl}
                target="_blank"
                rel="noopener nofollow"
                className="underline hover:text-slate-200"
              >
                {post.imageCredit.photographer}
              </a>
            ) : (
              post.imageCredit.photographer
            )}
            {post.imageCredit.source ? (
              <>
                {" / "}
                {post.imageCredit.sourceUrl ? (
                  <a
                    href={post.imageCredit.sourceUrl}
                    target="_blank"
                    rel="noopener nofollow"
                    className="underline hover:text-slate-200"
                  >
                    {post.imageCredit.source}
                  </a>
                ) : (
                  post.imageCredit.source
                )}
              </>
            ) : null}
          </p>
        ) : null}
      </section>

      <article className="bg-white py-12 sm:py-16">
        <div className={siteContainerLg}>
          <div className="max-w-4xl mx-auto lg:max-w-7xl lg:grid lg:grid-cols-[1fr_250px] lg:gap-12">
            <div className="max-w-4xl">
              <div className="mb-8 pb-8 border-b border-slate-200">
                <AuthorByline
                  authorSlug={authorSlug}
                  authorName={post.author}
                  publishedDate={post.date}
                  updatedDate={post.updatedDate}
                />
                <p className="mt-2 text-xs text-slate-500 max-w-xl">
                  Editorial content from the Holloway Davies team. For
                  decisions specific to your business,{" "}
                  <Link href="/contact" className="underline hover:text-orange-700">
                    book a call
                  </Link>
                  .
                </p>
              </div>

              {takeaways ? (
                <section
                  className="tldr not-prose rounded-lg border-l-4 border-orange-600 bg-slate-50 p-6"
                  aria-label="Key takeaways"
                >
                  <p className="text-xs font-bold uppercase tracking-wider text-orange-700">
                    Key takeaways
                  </p>
                  <ul className="mt-3 space-y-2">
                    {takeaways.map((t, i) => (
                      <li key={i} className="flex items-start gap-2 text-slate-800">
                        <span className="mt-2 h-1.5 w-1.5 rounded-full bg-orange-600 shrink-0" />
                        <span className="text-base leading-relaxed">{t}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              ) : post.summary ? (
                <section className="tldr" aria-label="Summary">
                  <p className="text-xs font-bold uppercase tracking-wider text-orange-700">
                    TL;DR
                  </p>
                  <p className="mt-2 text-lg text-slate-700 leading-relaxed border-l-4 border-orange-600 bg-slate-50 p-6">
                    {post.summary}
                  </p>
                </section>
              ) : null}

              <div className="lg:hidden mt-8">
                <TableOfContents headings={headings} />
              </div>

              <div
                className="article-body prose-blog mt-10"
                dangerouslySetInnerHTML={{ __html: post.contentHtml }}
              />

              <InlinePrompt
                source={`blog-${categorySlug}-${post.slug}`.slice(0, 80)}
                heading="Get the Director's Brief in your inbox."
                body={`One short email a week on UK tax for limited companies, contractors, sole traders and small businesses. Plain text, unsubscribe one click. Most useful when ${post.category.toLowerCase()} is on your mind.`}
              />

              {post.faqs && post.faqs.length > 0 ? (
                <section className="mt-16" aria-labelledby="faq-heading">
                  <h2 id="faq-heading" className="text-3xl font-bold text-slate-900 mb-8">
                    Frequently asked questions
                  </h2>
                  <dl className="space-y-4">
                    {post.faqs.map((faq, i) => (
                      <div key={i} className="border-l-4 border-slate-300 bg-slate-50 p-6">
                        <dt className="text-lg font-bold text-slate-900">{faq.question}</dt>
                        <dd className="mt-3 text-base text-slate-700 leading-relaxed">{faq.answer}</dd>
                      </div>
                    ))}
                  </dl>
                </section>
              ) : null}

              <aside className="mt-16 flex gap-5 items-start bg-slate-50 border border-slate-200 p-6 sm:p-8 rounded-lg">
                <div className="hidden sm:block shrink-0 w-14 h-14 rounded-full bg-orange-100 text-orange-700 flex items-center justify-center">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-bold uppercase tracking-wider text-orange-700">About the author</p>
                  <p className="mt-1 text-lg font-bold text-slate-900">{niche.display_name}</p>
                  <p className="mt-2 text-sm text-slate-600 leading-relaxed">{niche.description}</p>
                  <Link href="/about" className="mt-3 inline-block text-sm font-semibold text-orange-700 hover:text-orange-800">
                    Learn more about our team →
                  </Link>
                </div>
              </aside>

              <div className="mt-16 bg-slate-900 p-8 sm:p-10 text-white">
                <h2 className="text-2xl font-bold text-white sm:text-3xl">
                  {niche.blog.cta_heading}
                </h2>
                <p className="mt-4 text-base leading-relaxed text-slate-200">
                  {niche.blog.cta_body}
                </p>
                <div className="mt-8">
                  <LeadForm redirectOnSuccess={false} submitLabel={niche.blog.cta_button} />
                </div>
              </div>

              {related.length > 0 ? (
                <section className="mt-16" aria-labelledby="related-heading">
                  <h2 id="related-heading" className="text-2xl font-bold text-slate-900 mb-8">
                    Related articles
                  </h2>
                  <ul className="space-y-4">
                    {related.map((r) => (
                      <li key={r.slug}>
                        <Link
                          href={`/blog/${r.categorySlug}/${r.slug}`}
                          className="block border-l-4 border-slate-300 bg-slate-50 p-6 transition-all hover:border-orange-600 hover:bg-white hover:shadow-md"
                        >
                          <h3 className="text-lg font-bold text-slate-900">{r.title}</h3>
                          <p className="mt-2 text-sm text-slate-600">{r.summary}</p>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </section>
              ) : null}
            </div>

            <aside className="hidden lg:block">
              <div className="sticky top-24">
                <TableOfContents headings={headings} />
              </div>
            </aside>
          </div>
        </div>
      </article>
    </>
  );
}
