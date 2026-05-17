import fs from "fs";
import path from "path";
import matter from "gray-matter";
import type { BlogFrontmatter, BlogPost } from "@/types/blog";
import { addHeadingIds } from "./markdown-utils";

const postsDirectory = path.join(process.cwd(), "content", "blog");

function parsePostFile(filePath: string): BlogPost {
  const raw = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(raw);
  const fm = data as Partial<BlogFrontmatter>;

  if (!fm.slug || !fm.title) {
    throw new Error(`Invalid blog frontmatter in ${filePath}`);
  }

  const contentWithIds = addHeadingIds(content.trim());

  return {
    title: fm.title,
    slug: fm.slug,
    date: fm.date ?? "",
    updatedDate: fm.updatedDate,
    author: fm.author ?? "",
    authorSlug: fm.authorSlug,
    category: fm.category ?? "General",
    metaTitle: fm.metaTitle ?? fm.title,
    metaDescription: fm.metaDescription ?? "",
    altText: fm.altText,
    image: fm.image,
    imageCredit: fm.imageCredit,
    h1: fm.h1 ?? fm.title,
    summary: fm.summary ?? "",
    keyTakeaways: fm.keyTakeaways,
    schema: fm.schema,
    canonical: fm.canonical,
    faqs: fm.faqs,
    contentHtml: contentWithIds,
  };
}

export function getAllPosts(): BlogPost[] {
  if (!fs.existsSync(postsDirectory)) {
    return [];
  }
  const files = fs.readdirSync(postsDirectory).filter((f) => f.endsWith(".md"));
  const posts = files.map((file) =>
    parsePostFile(path.join(postsDirectory, file)),
  );
  return posts.sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime(),
  );
}

export function getPostBySlug(slug: string): BlogPost | null {
  const filePath = path.join(postsDirectory, `${slug}.md`);
  if (!fs.existsSync(filePath)) {
    return null;
  }
  return parsePostFile(filePath);
}

export function getRelatedPosts(
  currentSlug: string,
  category: string,
  limit = 3,
): BlogPost[] {
  if (!fs.existsSync(postsDirectory)) {
    return [];
  }

  const files = fs.readdirSync(postsDirectory).filter((f) => f.endsWith(".md"));
  const candidates: BlogPost[] = [];

  for (const file of files) {
    const filePath = path.join(postsDirectory, file);
    const raw = fs.readFileSync(filePath, "utf8");
    const { data } = matter(raw);
    const fm = data as Partial<BlogFrontmatter>;

    if (fm.slug === currentSlug) continue;
    if (fm.category !== category) continue;
    if (!fm.slug || !fm.title) continue;

    candidates.push(parsePostFile(filePath));
  }

  return candidates
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, limit);
}

export function slugifyCategory(category: string): string {
  return category
    .toLowerCase()
    .replace(/[()]/g, "")
    .replace(/&/g, "and")
    .replace(/\s+/g, "-")
    .replace(/--+/g, "-")
    .trim();
}

export function getCategorySlug(post: BlogPost): string {
  return slugifyCategory(post.category);
}

export function getPostByCategoryAndSlug(
  categorySlug: string,
  articleSlug: string,
): BlogPost | null {
  const post = getPostBySlug(articleSlug);
  if (!post) return null;
  if (getCategorySlug(post) !== categorySlug) return null;
  return post;
}

export function getAllCategories(): Array<{ slug: string; name: string; count: number }> {
  const posts = getAllPosts();
  const categoryMap = new Map<string, { name: string; count: number }>();

  for (const post of posts) {
    const slug = getCategorySlug(post);
    if (categoryMap.has(slug)) {
      categoryMap.get(slug)!.count++;
    } else {
      categoryMap.set(slug, { name: post.category, count: 1 });
    }
  }

  return Array.from(categoryMap.entries())
    .map(([slug, data]) => ({ slug, name: data.name, count: data.count }))
    .sort((a, b) => b.count - a.count);
}

export function calculateReadTime(html: string): number {
  const text = html.replace(/<[^>]*>/g, " ");
  const words = text.split(/\s+/).filter((w) => w.length > 0).length;
  return Math.max(1, Math.round(words / 238));
}
