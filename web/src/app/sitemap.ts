import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";
import { getAllPosts, getAllCategories, getCategorySlug } from "@/lib/blog";
import { getAllFundamentals } from "@/lib/fundamentals";
import { CITIES } from "@/app/locations/[slug]/data";
import { GLOSSARY } from "@/app/glossary/[slug]/data";
import { GUIDES } from "@/app/guides/[slug]/data";
import { TEAM } from "@/app/team/[slug]/data";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteConfig.url.replace(/\/$/, "");

  const staticPaths = [
    "",
    "/services",
    "/about",
    "/contact",
    "/free-health-check",
    "/incorporation",
    "/r-and-d-credits",
    "/guides",
    "/blog",
    "/fundamentals",
    "/calculators",
    "/calculators/salary-dividend-optimiser",
    "/calculators/take-home-pay-calculator",
    "/calculators/employer-ni-calculator",
    "/calculators/pension-contribution-optimiser",
    "/calculators/rd-tax-credit-estimator",
    "/calculators/badr-cgt-calculator",
    "/calculators/vat-scheme-comparator",
    "/locations",
    "/glossary",
    "/uk-tax-rates",
    "/newsletter",
    "/privacy-policy",
    "/terms",
    "/cookie-policy",
  ];

  const hreflang = (url: string) => ({
    languages: { "en-GB": url, "x-default": url },
  });

  const entries: MetadataRoute.Sitemap = staticPaths.map((path) => {
    const url = `${base}${path}`;
    return {
      url,
      lastModified: new Date(),
      changeFrequency: path === "/blog" ? "weekly" : "monthly",
      priority: path === "" ? 1 : 0.7,
      alternates: hreflang(url),
    };
  });

  const categories = getAllCategories();
  for (const cat of categories) {
    const url = `${base}/blog/${cat.slug}`;
    entries.push({
      url,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.8,
      alternates: hreflang(url),
    });
  }

  for (const post of getAllPosts()) {
    const categorySlug = getCategorySlug(post);
    const url = `${base}/blog/${categorySlug}/${post.slug}`;
    entries.push({
      url,
      lastModified: post.date ? new Date(post.date) : new Date(),
      changeFrequency: "monthly",
      priority: 0.8,
      alternates: hreflang(url),
    });
  }

  for (const guide of getAllFundamentals()) {
    const url = `${base}/fundamentals/${guide.slug}`;
    entries.push({
      url,
      lastModified: guide.date ? new Date(guide.date) : new Date(),
      changeFrequency: "monthly",
      priority: 0.9,
      alternates: hreflang(url),
    });
  }

  for (const slug of Object.keys(CITIES)) {
    const url = `${base}/locations/${slug}`;
    entries.push({
      url,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.85,
      alternates: hreflang(url),
    });
  }

  for (const slug of Object.keys(GLOSSARY)) {
    const url = `${base}/glossary/${slug}`;
    entries.push({
      url,
      lastModified: new Date(),
      changeFrequency: "yearly",
      priority: 0.6,
      alternates: hreflang(url),
    });
  }

  for (const slug of Object.keys(GUIDES)) {
    const url = `${base}/guides/${slug}`;
    entries.push({
      url,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.75,
      alternates: hreflang(url),
    });
  }

  for (const slug of Object.keys(TEAM)) {
    const url = `${base}/team/${slug}`;
    entries.push({
      url,
      lastModified: new Date(),
      changeFrequency: "yearly",
      priority: 0.5,
      alternates: hreflang(url),
    });
  }

  return entries;
}
