import { Metadata } from "next";
import { notFound } from "next/navigation";
import { getAllFundamentals, getFundamentalBySlug } from "@/lib/fundamentals";
import { siteConfig } from "@/config/site";
import { buildOgImageUrl } from "@/lib/schema";
import { FundamentalsRenderer } from "@/components/blog/FundamentalsRenderer";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  const posts = getAllFundamentals();
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = getFundamentalBySlug(slug);
  if (!post) return { title: "Guide Not Found" };

  return {
    title: post.metaTitle,
    description: post.metaDescription,
    alternates: {
      canonical: post.canonical,
      languages: {
        "en-GB": post.canonical,
        "x-default": post.canonical,
      },
    },
    openGraph: {
      title: post.metaTitle,
      description: post.metaDescription,
      type: "article",
      url: post.canonical,
      siteName: siteConfig.name,
      publishedTime: post.date,
      images: [
        {
          url: post.image || buildOgImageUrl(post.h1, post.category),
          width: 1200,
          height: 630,
          alt: post.altText || post.title,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: post.metaTitle,
      description: post.metaDescription,
      images: [post.image || buildOgImageUrl(post.h1, post.category)],
    },
  };
}

export default async function FundamentalPage({ params }: Props) {
  const { slug } = await params;
  const post = getFundamentalBySlug(slug);
  if (!post) notFound();

  const related = getAllFundamentals()
    .filter((p) => p.slug !== post.slug)
    .slice(0, 3)
    .map((r) => ({ slug: r.slug, title: r.title, summary: r.summary }));

  return <FundamentalsRenderer post={post} related={related} />;
}
