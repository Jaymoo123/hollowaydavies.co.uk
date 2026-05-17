import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import matter from "gray-matter";

export const dynamic = "force-static";
export const revalidate = 3600; // 1h

const contentRoot = () => path.join(process.cwd(), "content");

/**
 * Strip markdown to plain prose suitable for AI retrieval.
 * Keeps headings as `# ...` lines but removes images, link syntax,
 * code fences, and HTML comments.
 */
function flatten(md: string): string {
  return md
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/!\[[^\]]*]\([^)]*\)/g, "")
    .replace(/```[\s\S]*?```/g, "")
    .replace(/\[([^\]]+)]\([^)]+\)/g, "$1")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function readMarkdownDir(rel: string, prefix: string): string {
  const dir = path.join(contentRoot(), rel);
  if (!fs.existsSync(dir)) return "";
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
  const parts: string[] = [];
  for (const file of files) {
    const raw = fs.readFileSync(path.join(dir, file), "utf8");
    const { data, content } = matter(raw);
    const slug = (data.slug as string) || file.replace(/\.md$/, "");
    const title = (data.title as string) || slug;
    const summary = (data.summary as string) || (data.metaDescription as string) || "";
    const url = `https://www.hollowaydavies.co.uk/${prefix}/${slug}`;
    parts.push(
      [
        "",
        "================================================================",
        `URL: ${url}`,
        `Title: ${title}`,
        summary ? `Summary: ${summary}` : null,
        "================================================================",
        "",
        flatten(content),
      ]
        .filter(Boolean)
        .join("\n"),
    );
  }
  return parts.join("\n\n");
}

const HEADER = `# Holloway Davies, Full Content Reference

This file is a flat, machine-readable dump of every published guide and post on
hollowaydavies.co.uk. It exists for AI retrieval, training, and citation.
The structured index lives at https://www.hollowaydavies.co.uk/llms.txt
and the current tax rates JSON at /api/uk-tax-rates.json.

Editorial: all tax figures use 2025/26 UK rates as of the date below. Always
verify against gov.uk for time-sensitive decisions. For advice specific to a
given business, see https://www.hollowaydavies.co.uk/contact.

`;

export async function GET() {
  const generatedAt = new Date().toISOString();

  const sections: string[] = [HEADER, `Generated: ${generatedAt}\n`];

  const fundamentals = readMarkdownDir("fundamentals", "fundamentals");
  if (fundamentals) {
    sections.push("\n\n## PILLAR GUIDES\n\n", fundamentals);
  }

  const blog = readMarkdownDir("blog", "blog");
  if (blog) {
    sections.push("\n\n## BLOG POSTS\n\n", blog);
  }

  const body = sections.join("");

  return new NextResponse(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
      "X-Robots-Tag": "all",
    },
  });
}
