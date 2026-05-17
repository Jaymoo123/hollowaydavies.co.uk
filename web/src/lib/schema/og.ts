import { siteConfig } from "@/config/site";

/**
 * Build a dynamic OG image URL via the /api/og route.
 * Title is required; category is optional and produces the pill above the title.
 */
export function buildOgImageUrl(title: string, category?: string): string {
  const params = new URLSearchParams({ title });
  if (category) params.set("category", category);
  return `${siteConfig.url}/api/og?${params.toString()}`;
}
