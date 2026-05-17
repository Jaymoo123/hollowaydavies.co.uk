import type { Metadata } from "next";
import Link from "next/link";
import { siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { SignupForm } from "@/components/newsletter/SignupForm";
import { getAllPosts, calculateReadTime } from "@/lib/blog";
import { BlogListWithSearch } from "@/components/blog/BlogListWithSearch";
import { niche } from "@/config/niche-loader";

function slugifyCategory(category: string): string {
  return category
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export const metadata: Metadata = {
  title: `Insights | ${siteConfig.name}`,
  description:
    "Plain-English guidance on UK business tax, structure, payroll, VAT, R&D, MTD and exit planning. Written by ICAEW-qualified accountants. Updated for 2025/26 rates.",
  alternates: { canonical: `${siteConfig.url}/blog` },
  openGraph: {
    title: `Insights | ${siteConfig.name}`,
    description:
      "Plain-English guidance on UK business tax, structure, payroll, VAT and exit planning.",
    url: `${siteConfig.url}/blog`,
    type: "website",
  },
};

export default function BlogIndexPage() {
  const posts = getAllPosts();
  const enriched = posts.map((p) => ({ ...p, categorySlug: slugifyCategory(p.category) }));

  const readTimes = new Map<string, number>();
  for (const p of enriched) {
    readTimes.set(p.slug, calculateReadTime(p.contentHtml));
  }

  // Categories with post counts, ordered per niche config (matches nav).
  const categoryNames: string[] = (niche.content_strategy?.categories as string[]) || [];
  const categoryCounts = new Map<string, number>();
  for (const p of enriched) {
    categoryCounts.set(p.category, (categoryCounts.get(p.category) || 0) + 1);
  }
  const categories = categoryNames
    .map((name) => ({
      name,
      slug: slugifyCategory(name),
      count: categoryCounts.get(name) || 0,
    }))
    .filter((c) => c.count > 0);

  return (
    <>
      {/* Hero */}
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <div className="max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              Insights
            </p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl lg:text-6xl">
              UK business tax, plainly explained.
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-neutral-600 max-w-2xl">
              {posts.length} articles on UK limited company tax, sole trader self-assessment, VAT &amp; MTD, payroll, R&amp;D credits, incorporation, director pay and exit planning. Written or reviewed by an ICAEW-qualified accountant. Updated against current HMRC rates.
            </p>
          </div>
        </div>
      </section>

      {/* Stage quick filter */}
      <section className="border-t border-neutral-200 bg-white">
        <div className={siteContainerLg}>
          <div className="py-6">
            <p className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-3">
              Browse by stage
            </p>
            <nav aria-label="Browse by stage" className="flex flex-wrap gap-2">
              {[
                { slug: "starting-a-business", name: "Starting a business" },
                { slug: "running-a-business", name: "Running a business" },
                { slug: "scaling-a-business", name: "Scaling a business" },
                { slug: "exiting-a-business", name: "Exiting a business" },
              ].map((s) => (
                <Link
                  key={s.slug}
                  href={`/blog/stage/${s.slug}`}
                  className="inline-flex items-center gap-2 border border-neutral-300 bg-white px-3 py-1.5 text-sm font-medium text-neutral-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
                >
                  {s.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </section>

      {/* Category quick filter */}
      {categories.length > 0 && (
        <section className="border-y border-neutral-200 bg-white">
          <div className={siteContainerLg}>
            <div className="py-6">
              <p className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-3">
                Browse by category
              </p>
              <nav aria-label="Browse by category" className="flex flex-wrap gap-2">
                {categories.map((c) => (
                  <Link
                    key={c.slug}
                    href={`/blog/${c.slug}`}
                    className="inline-flex items-center gap-2 border border-neutral-300 bg-white px-3 py-1.5 text-sm font-medium text-neutral-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
                  >
                    {c.name}
                    <span className="text-xs font-mono text-neutral-500">{c.count}</span>
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </section>
      )}

      {/* Search + list */}
      <section className="bg-[#fafaf7] py-12 sm:py-16">
        <div className={siteContainerLg}>
          <BlogListWithSearch
            posts={enriched}
            categories={categories}
            readTimes={readTimes}
          />
        </div>
      </section>

      {/* Newsletter */}
      <section className="bg-white py-16">
        <div className={siteContainerLg}>
          <div className="mx-auto max-w-2xl">
            <SignupForm
              source="blog-index"
              variant="card"
              heading="The Director&rsquo;s Brief"
              body="One short email a week on UK business tax for limited company directors, contractors and sole traders. Plain text, unsubscribe one click."
              ctaLabel="Subscribe"
            />
          </div>
        </div>
      </section>
    </>
  );
}
