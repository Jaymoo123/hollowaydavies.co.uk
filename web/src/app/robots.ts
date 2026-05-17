import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";

/**
 * robots.txt, explicit allow-list for every major AI / search engine
 * crawler we want courting us. Explicit named rules beat the wildcard
 * because some bots only honour their own entry.
 *
 * Disallow list is deliberately minimal: thank-you (post-conversion only),
 * /api/og (image generation, wasteful for crawlers), /api/* mutating routes.
 */
export default function robots(): MetadataRoute.Robots {
  const base = siteConfig.url.replace(/\/$/, "");

  const aiAndSearchBots = [
    // Google
    "Googlebot",
    "Googlebot-Image",
    "Googlebot-News",
    "Google-Extended",
    "GoogleOther",
    // OpenAI
    "GPTBot",
    "OAI-SearchBot",
    "ChatGPT-User",
    // Anthropic
    "ClaudeBot",
    "anthropic-ai",
    "Claude-Web",
    "Claude-SearchBot",
    "Claude-User",
    // Perplexity
    "PerplexityBot",
    "Perplexity-User",
    // Apple
    "Applebot",
    "Applebot-Extended",
    // Meta
    "Meta-ExternalAgent",
    "Meta-ExternalFetcher",
    "FacebookBot",
    "facebookexternalhit",
    // Microsoft / Bing
    "bingbot",
    "msnbot",
    "adidxbot",
    // DuckDuckGo
    "DuckAssistBot",
    "DuckDuckBot",
    // Mistral
    "MistralAI-User",
    // You.com
    "YouBot",
    // Cohere
    "cohere-ai",
    "cohere-training-data-crawler",
    // Brave
    "BraveBot",
    // ByteDance / TikTok
    "Bytespider",
    // Common Crawl (training data for many models)
    "CCBot",
    // Diffbot (Apple / many AI pipelines)
    "Diffbot",
    // Amazon (Alexa, Rufus)
    "Amazonbot",
    // Yandex
    "YandexBot",
    "YandexImages",
    // Naver
    "Yeti",
    // Seznam
    "SeznamBot",
    // Mojeek (independent index)
    "MojeekBot",
    // Ahrefs / Yep
    "AhrefsBot",
    "YepBot",
    // Social previews (helps OG card rendering)
    "Twitterbot",
    "LinkedInBot",
    "Slackbot",
    "Discordbot",
    "WhatsApp",
    "TelegramBot",
  ];

  const disallow = ["/thank-you", "/api/og", "/api/health-check/submit", "/api/newsletter/"];

  return {
    rules: [
      { userAgent: "*", allow: "/", disallow },
      ...aiAndSearchBots.map((userAgent) => ({
        userAgent,
        allow: "/",
        disallow,
      })),
    ],
    sitemap: `${base}/sitemap.xml`,
    host: base,
  };
}
