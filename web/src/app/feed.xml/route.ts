import { NextResponse } from "next/server";
import { getAllPosts, getCategorySlug } from "@/lib/blog";
import { siteConfig } from "@/config/site";

export const dynamic = "force-static";
export const revalidate = 3600;

function escape(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export async function GET() {
  const base = siteConfig.url.replace(/\/$/, "");
  const posts = getAllPosts()
    .filter((p) => p.date)
    .sort((a, b) => (a.date < b.date ? 1 : -1))
    .slice(0, 50);

  const lastBuildDate = posts[0]?.date
    ? new Date(posts[0].date).toUTCString()
    : new Date().toUTCString();

  const items = posts
    .map((p) => {
      const url = `${base}/blog/${getCategorySlug(p)}/${p.slug}`;
      const pubDate = p.date ? new Date(p.date).toUTCString() : new Date().toUTCString();
      const description = escape(p.metaDescription || p.summary || "");
      return `    <item>
      <title>${escape(p.title)}</title>
      <link>${url}</link>
      <guid isPermaLink="true">${url}</guid>
      <pubDate>${pubDate}</pubDate>
      <description>${description}</description>
      <category>${escape(p.category)}</category>
      ${p.author ? `<dc:creator>${escape(p.author)}</dc:creator>` : ""}
    </item>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>${escape(siteConfig.name)}</title>
    <link>${base}</link>
    <description>${escape(siteConfig.description)}</description>
    <language>en-GB</language>
    <lastBuildDate>${lastBuildDate}</lastBuildDate>
    <atom:link href="${base}/feed.xml" rel="self" type="application/rss+xml" />
${items}
  </channel>
</rss>
`;

  return new NextResponse(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
      "X-Robots-Tag": "all",
    },
  });
}
