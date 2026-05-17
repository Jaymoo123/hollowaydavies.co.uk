import Link from "next/link";
import Image from "next/image";
import type { BlogPost } from "@/types/blog";

type Props = {
  post: BlogPost;
  categorySlug: string;
  readTime: number;
};

export function BlogPostCard({ post, categorySlug, readTime }: Props) {
  const href = `/blog/${categorySlug}/${post.slug}`;
  return (
    <article className="h-full">
      <Link
        href={href}
        className="group flex h-full flex-col overflow-hidden border border-slate-200 bg-white shadow-sm transition-all hover:border-orange-600 hover:shadow-md"
      >
        <div className="relative h-44 overflow-hidden bg-slate-100">
          {post.image ? (
            <>
              <Image
                src={post.image}
                alt={post.altText || post.title}
                fill
                sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                className="object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-slate-900/15" />
            </>
          ) : (
            <div className="absolute inset-0 bg-gradient-to-br from-orange-100 to-slate-100" />
          )}
          <div className="absolute bottom-3 left-3 bg-orange-600 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-white">
            Article
          </div>
        </div>

        <div className="flex flex-1 flex-col p-6">
          <h2 className="text-lg font-bold leading-snug text-slate-900 transition-colors group-hover:text-orange-700">
            {post.title}
          </h2>
          {post.summary && (
            <p className="mt-3 line-clamp-3 flex-grow text-sm text-slate-600">{post.summary}</p>
          )}
          <div className="mt-4 flex items-center gap-3 border-t border-slate-100 pt-4 text-xs text-slate-500">
            {post.date && (
              <time dateTime={post.date}>
                {new Intl.DateTimeFormat("en-GB", {
                  day: "numeric",
                  month: "short",
                  year: "numeric",
                }).format(new Date(post.date))}
              </time>
            )}
            <span aria-hidden="true">·</span>
            <span>{readTime} min read</span>
          </div>
        </div>
      </Link>
    </article>
  );
}
