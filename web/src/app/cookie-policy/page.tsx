import type { Metadata } from "next";
import { contentNarrow, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { Breadcrumb } from "@/components/ui/Breadcrumb";

export const metadata: Metadata = {
  title: "Cookie policy",
  description: `How ${siteConfig.name} uses cookies and similar technologies. Google Analytics cookies explained.`,
  alternates: { canonical: `${siteConfig.url}/cookie-policy` },
  openGraph: {
    title: `Cookie Policy | ${siteConfig.name}`,
    description: `How ${siteConfig.name} uses cookies and similar technologies. Google Analytics cookies explained.`,
    url: `${siteConfig.url}/cookie-policy`,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Cookie policy",
    description: `How ${siteConfig.name} uses cookies and similar technologies. Google Analytics cookies explained.`,
  },
};

export default function CookiePolicyPage() {
  return (
    <div className={`${contentNarrow} ${sectionY}`}>
      <Breadcrumb
        items={[
          { label: "Home", href: "/" },
          { label: "Cookie policy" },
        ]}
      />
      <h1 className="font-serif text-3xl font-semibold text-[var(--ink)] sm:text-4xl">Cookie policy</h1>
      <p className="mt-4 text-sm text-[var(--muted)]">Last updated: 27 March 2026</p>
      <div className="prose-blog mt-8 space-y-6 text-[var(--ink-soft)]">
        <p>
          This policy describes how {siteConfig.name} uses cookies and similar technologies on our website. Cookies are small text files stored on your device that help us understand how visitors use our Site and improve your experience.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">1. What cookies we use</h2>
        
        <h3 className="mt-4 text-lg font-semibold text-[var(--ink)]">Essential cookies</h3>
        <p>
          We do not currently use any strictly necessary cookies. Our Site functions without requiring cookies for basic operation.
        </p>

        <h3 className="mt-4 text-lg font-semibold text-[var(--ink)]">Analytics cookies (Google Analytics)</h3>
        <p>
          We use Google Analytics to understand how visitors interact with our Site. This helps us improve content and user experience. Google Analytics sets the following cookies:
        </p>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong>_ga:</strong> Distinguishes unique users. Expires after 2 years.
          </li>
          <li>
            <strong>_gid:</strong> Distinguishes unique users. Expires after 24 hours.
          </li>
          <li>
            <strong>_gat_gtag_*:</strong> Used to throttle request rate. Expires after 1 minute.
          </li>
        </ul>
        <p>
          Google Analytics collects information such as pages visited, time spent on pages, browser type, device type, and referral source. IP addresses are anonymised. Data is retained for 14 months.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">2. Purpose of cookies</h2>
        <p>We use cookies to:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>Understand which pages are most useful to UK business owners and visitors</li>
          <li>Identify technical issues or broken links</li>
          <li>Measure the effectiveness of our content</li>
          <li>Improve the overall user experience</li>
        </ul>
        <p>
          We do <strong>not</strong> use cookies for advertising, remarketing, or selling your data to third parties.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">3. How to manage cookies</h2>
        <p>You can control and manage cookies in several ways:</p>

        <h3 className="mt-4 text-lg font-semibold text-[var(--ink)]">Browser settings</h3>
        <p>
          Most browsers allow you to block or delete cookies through their settings. Please note that blocking all cookies may affect your experience on some websites. Instructions for popular browsers:
        </p>
        <ul className="list-disc space-y-1 pl-6">
          <li>
            <a
              href="https://support.google.com/chrome/answer/95647"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--accent-strong)] underline"
            >
              Google Chrome
            </a>
          </li>
          <li>
            <a
              href="https://support.mozilla.org/en-US/kb/enhanced-tracking-protection-firefox-desktop"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--accent-strong)] underline"
            >
              Mozilla Firefox
            </a>
          </li>
          <li>
            <a
              href="https://support.apple.com/en-gb/guide/safari/sfri11471/mac"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--accent-strong)] underline"
            >
              Safari
            </a>
          </li>
          <li>
            <a
              href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--accent-strong)] underline"
            >
              Microsoft Edge
            </a>
          </li>
        </ul>

        <h3 className="mt-4 text-lg font-semibold text-[var(--ink)]">Google Analytics opt-out</h3>
        <p>
          You can opt out of Google Analytics tracking by installing the{" "}
          <a
            href="https://tools.google.com/dlpage/gaoptout"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--accent-strong)] underline"
          >
            Google Analytics Opt-out Browser Add-on
          </a>
          .
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">4. Changes to this policy</h2>
        <p>
          We may update this cookie policy from time to time. The &quot;Last updated&quot; date at the top of this page shows when it was last revised.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">5. Contact us</h2>
        <p>
          If you have questions about our use of cookies, please contact us at{" "}
          <a href={`mailto:${siteConfig.contact.email}`} className="text-[var(--accent-strong)] underline">
            {siteConfig.contact.email}
          </a>
          .
        </p>
      </div>
    </div>
  );
}
