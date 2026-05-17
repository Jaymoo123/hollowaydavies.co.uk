import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { getAllPosts, calculateReadTime } from "@/lib/blog";
import { BlogListWithSearch } from "@/components/blog/BlogListWithSearch";
import { niche } from "@/config/niche-loader";
import { Breadcrumb } from "@/components/ui/Breadcrumb";

function slugifyCategory(category: string): string {
  return category
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/^-+|-+$/g, "");
}

type Props = { params: Promise<{ category: string }> };

export async function generateStaticParams() {
  const categoryNames: string[] = (niche.content_strategy?.categories as string[]) || [];
  return categoryNames.map((name) => ({ category: slugifyCategory(name) }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await params;
  const categoryNames: string[] = (niche.content_strategy?.categories as string[]) || [];
  const match = categoryNames.find((n) => slugifyCategory(n) === category);
  if (!match) return { title: "Category not found" };
  const url = `${siteConfig.url}/blog/${category}`;
  return {
    title: `${match} articles | ${siteConfig.name}`,
    description: `${match} articles for UK business owners. Written by ICAEW-qualified accountants, updated for 2025/26 rates.`,
    alternates: { canonical: url },
    openGraph: {
      title: `${match} articles | ${siteConfig.name}`,
      description: `${match} articles for UK business owners.`,
      url,
      type: "website",
    },
  };
}

export default async function BlogCategoryPage({ params }: Props) {
  const { category } = await params;
  const categoryNames: string[] = (niche.content_strategy?.categories as string[]) || [];
  const matchedName = categoryNames.find((n) => slugifyCategory(n) === category);
  if (!matchedName) notFound();

  const allPosts = getAllPosts();
  const enriched = allPosts
    .filter((p) => p.category === matchedName)
    .map((p) => ({ ...p, categorySlug: category }));

  if (enriched.length === 0) notFound();

  const readTimes = new Map<string, number>();
  for (const p of enriched) {
    readTimes.set(p.slug, calculateReadTime(p.contentHtml));
  }

  // Build sibling category list for cross-navigation
  const siblingCounts = new Map<string, number>();
  for (const p of allPosts) {
    siblingCounts.set(p.category, (siblingCounts.get(p.category) || 0) + 1);
  }
  const siblings = categoryNames
    .map((name) => ({
      name,
      slug: slugifyCategory(name),
      count: siblingCounts.get(name) || 0,
    }))
    .filter((c) => c.count > 0);

  return (
    <>
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <Breadcrumb
            items={[
              { label: "Home", href: "/" },
              { label: "Insights", href: "/blog" },
              { label: matchedName },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              {matchedName}
            </p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl">
              {matchedName}
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-neutral-600 max-w-2xl">
              {enriched.length} article{enriched.length !== 1 ? "s" : ""} on {matchedName.toLowerCase()} for UK limited company directors, contractors, sole traders and small businesses.
            </p>
          </div>
        </div>
      </section>

      {/* Sibling category quick switch */}
      <section className="border-y border-neutral-200 bg-white">
        <div className={siteContainerLg}>
          <nav aria-label="Other categories" className="flex flex-wrap gap-2 py-6">
            <Link
              href="/blog"
              className="inline-flex items-center gap-2 border border-neutral-300 bg-white px-3 py-1.5 text-sm font-medium text-neutral-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
            >
              All
            </Link>
            {siblings.map((c) => (
              <Link
                key={c.slug}
                href={`/blog/${c.slug}`}
                className={
                  c.slug === category
                    ? "inline-flex items-center gap-2 border border-orange-600 bg-orange-50 px-3 py-1.5 text-sm font-semibold text-orange-700"
                    : "inline-flex items-center gap-2 border border-neutral-300 bg-white px-3 py-1.5 text-sm font-medium text-neutral-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
                }
              >
                {c.name}
                <span className="text-xs font-mono text-neutral-500">{c.count}</span>
              </Link>
            ))}
          </nav>
        </div>
      </section>

      <section className="bg-[#fafaf7] py-12 sm:py-16">
        <div className={siteContainerLg}>
          <BlogListWithSearch
            posts={enriched}
            categories={siblings}
            readTimes={readTimes}
            activeCategory={category}
          />
        </div>
      </section>
    </>
  );
}
