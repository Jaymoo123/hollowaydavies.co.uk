import type { Metadata, Viewport } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";
import { PageShell } from "@/components/layout/PageShell";
import { GoogleAnalytics } from "@/components/analytics/GoogleAnalytics";
import { siteConfig } from "@/config/site";
import { niche } from "@/config/niche-loader";

const siteUrl = siteConfig.url;

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: niche.seo.theme_color,
};

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: `${siteConfig.name} | ${siteConfig.tagline}`,
    template: `%s | ${siteConfig.name}`,
  },
  description: siteConfig.description,
  alternates: {
    canonical: siteUrl,
    languages: {
      "en-GB": siteUrl,
      "x-default": siteUrl,
    },
  },
  verification: {
    google: niche.seo.search_console_verification.google || undefined,
    yandex: niche.seo.search_console_verification.yandex || undefined,
    other: {
      ...(niche.seo.search_console_verification.bing
        ? { "msvalidate.01": niche.seo.search_console_verification.bing }
        : {}),
      ...(niche.seo.search_console_verification.naver
        ? { "naver-site-verification": niche.seo.search_console_verification.naver }
        : {}),
      ...(niche.seo.search_console_verification.pinterest
        ? { "p:domain_verify": niche.seo.search_console_verification.pinterest }
        : {}),
    },
  },
  openGraph: {
    type: "website",
    locale: siteConfig.locale,
    url: siteUrl,
    siteName: siteConfig.name,
    title: siteConfig.name,
    description: siteConfig.description,
    images: [{ url: siteConfig.publisherLogoUrl, alt: siteConfig.name }],
  },
  twitter: {
    card: "summary_large_image",
    title: siteConfig.name,
    description: siteConfig.description,
    images: [siteConfig.publisherLogoUrl],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en-GB" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <head>
        <GoogleAnalytics measurementId={niche.seo.google_analytics_id} />
      </head>
      <body className="antialiased font-sans">
        <PageShell>{children}</PageShell>
      </body>
    </html>
  );
}
