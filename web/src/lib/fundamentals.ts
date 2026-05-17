import fs from "fs";
import path from "path";
import matter from "gray-matter";
import type { BlogFrontmatter, BlogPost } from "@/types/blog";
import { addHeadingIds } from "./markdown-utils";

const fundamentalsDirectory = path.join(process.cwd(), "content", "fundamentals");

function parseFile(filePath: string): BlogPost {
  const raw = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(raw);
  const fm = data as Partial<BlogFrontmatter>;

  if (!fm.slug || !fm.title) {
    throw new Error(`Invalid fundamental frontmatter in ${filePath}`);
  }

  const contentWithIds = addHeadingIds(content.trim());

  return {
    title: fm.title,
    slug: fm.slug,
    date: fm.date ?? "",
    author: fm.author ?? "",
    category: fm.category ?? "General",
    metaTitle: fm.metaTitle ?? fm.title,
    metaDescription: fm.metaDescription ?? "",
    altText: fm.altText,
    image: fm.image,
    imageCredit: fm.imageCredit,
    h1: fm.h1 ?? fm.title,
    summary: fm.summary ?? "",
    schema: fm.schema,
    canonical: fm.canonical,
    faqs: fm.faqs,
    contentHtml: contentWithIds,
  };
}

export function getAllFundamentals(): BlogPost[] {
  if (!fs.existsSync(fundamentalsDirectory)) {
    return [];
  }
  const files = fs.readdirSync(fundamentalsDirectory).filter((f) => f.endsWith(".md"));
  const posts = files.map((file) => parseFile(path.join(fundamentalsDirectory, file)));
  return posts.sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime(),
  );
}

export function getFundamentalBySlug(slug: string): BlogPost | null {
  const filePath = path.join(fundamentalsDirectory, `${slug}.md`);
  if (!fs.existsSync(filePath)) {
    return null;
  }
  return parseFile(filePath);
}
