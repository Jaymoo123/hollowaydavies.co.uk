import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { getAllPosts, calculateReadTime } from "@/lib/blog";
import { BlogListWithSearch } from "@/components/blog/BlogListWithSearch";
import { Breadcrumb } from "@/components/ui/Breadcrumb";
import type { BlogPost } from "@/types/blog";

function slugifyCategory(category: string): string {
  return category
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/^-+|-+$/g, "");
}

type Stage = {
  slug: string;
  name: string;
  intro: string;
  longIntro: string;
  // Categories that count as "this stage" content. Each post can appear in
  // multiple stages — that's intentional, the same content serves different
  // intents.
  categories: string[];
  // Title-level keyword filters (lowercase substrings) that promote a post
  // into this stage regardless of its tax category.
  titleKeywords?: string[];
};

const STAGES: Record<string, Stage> = {
  "starting-a-business": {
    slug: "starting-a-business",
    name: "Starting a business",
    intro: "You're about to register or just have.",
    longIntro:
      "If you're deciding between sole trader and limited company, registering for self-assessment, incorporating, or thinking about VAT registration for the first time, these are the articles to read first.",
    categories: ["Incorporation and Structure", "Sole Trader and Self Employment"],
    titleKeywords: ["register", "set up", "start", "incorporat", "sole trader vs", "first 90 days", "company formation"],
  },
  "running-a-business": {
    slug: "running-a-business",
    name: "Running a business",
    intro: "You're up and running. Now the day-to-day tax, payroll and bookkeeping decisions.",
    longIntro:
      "Bookkeeping, payroll, VAT returns, corporation tax, dividends and director pay — the operational tax and finance decisions that come up every month, quarter or year once your business is trading.",
    categories: [
      "Bookkeeping and Compliance",
      "VAT and Making Tax Digital",
      "Payroll and PAYE",
      "Corporation Tax",
      "Director Pay and Dividends",
      "Limited Company Tax",
    ],
  },
  "scaling-a-business": {
    slug: "scaling-a-business",
    name: "Scaling a business",
    intro: "You're hiring, claiming R&D, restructuring, or considering a holding company.",
    longIntro:
      "Once your business has stable trading profits, you face a different set of tax questions: how to structure for growth, when R&D credits are worth claiming, how to add directors and shareholders, when a holding company makes sense, and how to plan for the next stage.",
    categories: ["R&D Tax Credits", "Incorporation and Structure"],
    titleKeywords: ["hiring", "holding company", "alphabet share", "growth", "restructur", "r&d", "scaling", "associated compan"],
  },
  "exiting-a-business": {
    slug: "exiting-a-business",
    name: "Exiting a business",
    intro: "You're selling, winding down, or planning your exit in the next 18-24 months.",
    longIntro:
      "BADR planning, MVL vs strike-off, earn-out structures, goodwill valuation, due diligence preparation. The decisions you make 12-24 months before exit are where the real tax saving (or loss) happens.",
    categories: ["Exit and Capital Gains"],
    titleKeywords: ["badr", "exit", "selling", "mvl", "members voluntary", "earn-out", "goodwill", "due diligence", "close a limited"],
  },
};


export async function generateStaticParams() {
  return Object.keys(STAGES).map((stage) => ({ stage }));
}

type Props = { params: Promise<{ stage: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { stage } = await params;
  const s = STAGES[stage];
  if (!s) return { title: "Stage not found" };
  const url = `${siteConfig.url}/blog/stage/${stage}`;
  return {
    title: `${s.name} | Insights | ${siteConfig.name}`,
    description: `UK tax, structure and finance articles for ${s.name.toLowerCase()}. Written by editorial team, reviewed by ICAEW Chartered Accountant.`,
    alternates: { canonical: url },
    openGraph: {
      title: `${s.name} | Insights | ${siteConfig.name}`,
      description: s.intro,
      url,
      type: "website",
    },
  };
}

function postMatchesStage(post: BlogPost, stage: Stage): boolean {
  if (stage.categories.includes(post.category)) return true;
  if (stage.titleKeywords) {
    const t = (post.title + " " + post.summary).toLowerCase();
    if (stage.titleKeywords.some((k) => t.includes(k))) return true;
  }
  return false;
}

export default async function BlogStagePage({ params }: Props) {
  const { stage } = await params;
  const s = STAGES[stage];
  if (!s) notFound();

  const allPosts = getAllPosts();
  const filtered = allPosts.filter((p) => postMatchesStage(p, s));
  const enriched = filtered.map((p) => ({ ...p, categorySlug: slugifyCategory(p.category) }));

  const readTimes = new Map<string, number>();
  for (const p of enriched) {
    readTimes.set(p.slug, calculateReadTime(p.contentHtml));
  }

  const categoryCounts = new Map<string, number>();
  for (const p of enriched) {
    categoryCounts.set(p.category, (categoryCounts.get(p.category) || 0) + 1);
  }
  const categories = Array.from(categoryCounts.entries()).map(([name, count]) => ({
    name,
    slug: slugifyCategory(name),
    count,
  }));

  return (
    <>
      <section className={`${sectionY} bg-[#fafaf7]`}>
        <div className={siteContainerLg}>
          <Breadcrumb
            items={[
              { label: "Home", href: "/" },
              { label: "Insights", href: "/blog" },
              { label: "By stage", href: "/blog/stage" },
              { label: s.name },
            ]}
          />
          <div className="mt-6 max-w-3xl">
            <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
              {s.intro}
            </p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl">
              {s.name}
            </h1>
            <p className="mt-6 text-lg leading-relaxed text-neutral-600 max-w-2xl">
              {s.longIntro}
            </p>
          </div>
        </div>
      </section>

      <section className="border-y border-neutral-200 bg-white">
        <div className={siteContainerLg}>
          <nav aria-label="Browse by stage" className="flex flex-wrap gap-2 py-6">
            {Object.values(STAGES).map((stg) => (
              <Link
                key={stg.slug}
                href={`/blog/stage/${stg.slug}`}
                className={
                  stg.slug === s.slug
                    ? "inline-flex items-center gap-2 border border-orange-600 bg-orange-50 px-3 py-1.5 text-sm font-semibold text-orange-700"
                    : "inline-flex items-center gap-2 border border-neutral-300 bg-white px-3 py-1.5 text-sm font-medium text-neutral-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
                }
              >
                {stg.name}
              </Link>
            ))}
            <Link
              href="/blog"
              className="ml-2 inline-flex items-center gap-2 border border-neutral-300 bg-white px-3 py-1.5 text-sm font-medium text-neutral-700 transition-colors hover:border-orange-600 hover:bg-orange-50 hover:text-orange-700"
            >
              All articles
            </Link>
          </nav>
        </div>
      </section>

      <section className="bg-[#fafaf7] py-12 sm:py-16">
        <div className={siteContainerLg}>
          <p className="mb-6 text-sm text-neutral-600 font-mono">
            {enriched.length} article{enriched.length !== 1 ? "s" : ""} matched for {s.name.toLowerCase()}
          </p>
          <BlogListWithSearch
            posts={enriched}
            categories={categories}
            readTimes={readTimes}
            activeCategory={undefined}
          />
        </div>
      </section>
    </>
  );
}
