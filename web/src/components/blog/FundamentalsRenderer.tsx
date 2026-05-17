import Link from "next/link";
import Image from "next/image";
import type { BlogPost } from "@/types/blog";
import { LeadForm } from "@/components/forms/LeadForm";
import { buildArticleJsonLd } from "@/lib/schema";
import { siteContainerLg } from "@/components/ui/layout-utils";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import { niche } from "@/config/niche-loader";
import { TableOfContents } from "@/components/blog/TableOfContents";
import { ReadingProgress } from "@/components/blog/ReadingProgress";
import { extractHeadings } from "@/lib/markdown-utils";
import { calculateReadTime } from "@/lib/blog";

type FundamentalsRendererProps = {
  post: BlogPost;
  related?: { slug: string; title: string; summary: string }[];
};

function formatUkDate(isoDate: string): string {
  const d = new Date(isoDate);
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}

export function FundamentalsRenderer({ post, related = [] }: FundamentalsRendererProps) {
  const headings = extractHeadings(post.contentHtml);
  const readTime = calculateReadTime(post.contentHtml);
  const jsonLd =
    post.schema?.trim() ||
    buildArticleJsonLd(post, `/fundamentals/${post.slug}`);

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
        <div className="absolute inset-0 bg-slate-900/75" />
        <div className={`${siteContainerLg} relative z-10 h-full flex items-end pb-10 sm:pb-14`}>
          <div className="max-w-4xl">
            <Breadcrumb
              variant="light"
              items={[
                { label: "Home", href: "/" },
                { label: "Guides", href: "/fundamentals" },
                { label: "Fundamentals", href: "/fundamentals" },
                { label: post.title },
              ]}
            />
            <p className="mt-6 inline-block bg-orange-600 text-white text-xs font-bold uppercase tracking-wider px-3 py-1">
              Pillar Guide · {post.category}
            </p>
            <h1 className="mt-4 text-3xl font-bold leading-tight text-white sm:text-4xl md:text-5xl">
              {post.h1}
            </h1>
            <p className="mt-4 text-sm text-slate-300">
              {post.date && (
                <time dateTime={post.date}>{formatUkDate(post.date)}</time>
              )}
              {post.author ? (
                <>
                  {" · "}
                  <span>{post.author}</span>
                </>
              ) : null}
              {readTime > 0 && (
                <>
                  {" · "}
                  <span>{readTime} min read</span>
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
              {post.summary ? (
                <p className="text-lg text-slate-700 leading-relaxed border-l-4 border-orange-600 bg-slate-50 p-6">
                  {post.summary}
                </p>
              ) : null}

              <div className="lg:hidden mt-8">
                <TableOfContents headings={headings} />
              </div>

              <div
                className="article-body prose-blog mt-10"
                dangerouslySetInnerHTML={{ __html: post.contentHtml }}
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
                  <p className="text-sm font-bold uppercase tracking-wider text-orange-700">About this guide</p>
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
                    Other pillar guides
                  </h2>
                  <ul className="space-y-4">
                    {related.map((r) => (
                      <li key={r.slug}>
                        <Link
                          href={`/fundamentals/${r.slug}`}
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
