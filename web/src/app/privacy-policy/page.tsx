import type { Metadata } from "next";
import { contentNarrow, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { Breadcrumb } from "@/components/ui/Breadcrumb";

export const metadata: Metadata = {
  title: "Privacy policy",
  description: `How ${siteConfig.name} collects and uses personal data on this website. UK GDPR compliant.`,
  alternates: { canonical: `${siteConfig.url}/privacy-policy` },
  openGraph: {
    title: `Privacy Policy | ${siteConfig.name}`,
    description: `How ${siteConfig.name} collects and uses personal data on this website. UK GDPR compliant.`,
    url: `${siteConfig.url}/privacy-policy`,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Privacy policy",
    description: `How ${siteConfig.name} collects and uses personal data on this website. UK GDPR compliant.`,
  },
};

export default function PrivacyPolicyPage() {
  return (
    <div className={`${contentNarrow} ${sectionY}`}>
      <Breadcrumb
        items={[
          { label: "Home", href: "/" },
          { label: "Privacy policy" },
        ]}
      />
      <h1 className="font-serif text-3xl font-semibold text-[var(--ink)] sm:text-4xl">Privacy policy</h1>
      <p className="mt-4 text-sm text-[var(--muted)]">Last updated: 27 March 2026</p>
      <div className="prose-blog mt-8 space-y-6 text-[var(--ink-soft)]">
        <p>
          This policy explains how {siteConfig.legalName} (&quot;we&quot;, &quot;us&quot;, &quot;our&quot;) collects, uses, and protects your personal information when you use {siteConfig.name} (the &quot;Site&quot;). We are committed to protecting your privacy and complying with the UK General Data Protection Regulation (UK GDPR) and the Data Protection Act 2018.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">1. Data controller</h2>
        <p>
          {siteConfig.legalName} is the data controller responsible for your personal data. You can contact us at{" "}
          <a href={`mailto:${siteConfig.contact.email}`} className="text-[var(--accent-strong)] underline">
            {siteConfig.contact.email}
          </a>{" "}
          or by using the contact details on our <a href="/contact" className="text-[var(--accent-strong)] underline">contact page</a>.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">2. What information we collect</h2>
        <p>We may collect the following types of personal information:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong>Contact form submissions:</strong> When you submit an enquiry through our contact form, we collect your full name, email address, phone number, business type (e.g., limited company, sole trader, partnership, contractor), message content, and the URL of the page you submitted from.
          </li>
          <li>
            <strong>Analytics data:</strong> We use Google Analytics to understand how visitors use our Site. This includes your IP address (anonymised), browser type, device type, pages visited, time spent on pages, and referral source. Google Analytics uses cookies to collect this information.
          </li>
          <li>
            <strong>Technical data:</strong> Our hosting provider (Vercel) may log your IP address, browser type, and request data for security and performance purposes.
          </li>
        </ul>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">3. How we use your information</h2>
        <p>We use your personal information for the following purposes:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong>Responding to enquiries:</strong> To respond to your contact form submission and arrange an initial consultation (legal basis: legitimate interest in providing services you&apos;ve requested).
          </li>
          <li>
            <strong>Improving our Site:</strong> To understand how visitors use our Site and improve its content and functionality (legal basis: legitimate interest in improving our services).
          </li>
          <li>
            <strong>Compliance:</strong> To comply with legal obligations, such as record-keeping requirements for professional services firms.
          </li>
        </ul>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">4. How we store and protect your data</h2>
        <p>
          <strong>Contact form submissions</strong> are stored securely in Supabase, a PostgreSQL database service hosted in the EU. Access is restricted to authorised staff only. We retain enquiry data for up to 2 years to maintain a record of client relationships and comply with professional indemnity insurance requirements.
        </p>
        <p>
          <strong>Analytics data</strong> is processed by Google Analytics and retained for 14 months. Google&apos;s data processing is governed by their{" "}
          <a
            href="https://policies.google.com/privacy"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--accent-strong)] underline"
          >
            privacy policy
          </a>{" "}
          and our data processing agreement with Google.
        </p>
        <p>
          <strong>Hosting data</strong> is processed by Vercel Inc. (USA). Vercel is certified under the EU-US Data Privacy Framework. Logs are retained for security purposes only and are not used for marketing.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">5. Third-party services</h2>
        <p>We use the following third-party services that may process your personal data:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong>Supabase:</strong> Database and API for contact form submissions (EU-hosted, GDPR-compliant).
          </li>
          <li>
            <strong>Google Analytics:</strong> Website analytics and performance measurement. See our{" "}
            <a href="/cookie-policy" className="text-[var(--accent-strong)] underline">
              cookie policy
            </a>{" "}
            for details on how to opt out.
          </li>
          <li>
            <strong>Vercel:</strong> Website hosting and content delivery (USA, EU-US Data Privacy Framework certified).
          </li>
        </ul>
        <p>
          These third parties are contractually required to protect your data and use it only for the purposes we specify.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">6. Your rights under UK GDPR</h2>
        <p>You have the following rights regarding your personal data:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            <strong>Right of access:</strong> You can request a copy of the personal data we hold about you.
          </li>
          <li>
            <strong>Right to rectification:</strong> You can ask us to correct inaccurate or incomplete data.
          </li>
          <li>
            <strong>Right to erasure:</strong> You can request that we delete your personal data in certain circumstances (e.g., if it&apos;s no longer necessary for the purpose it was collected).
          </li>
          <li>
            <strong>Right to restrict processing:</strong> You can ask us to limit how we use your data in certain situations.
          </li>
          <li>
            <strong>Right to data portability:</strong> You can request a copy of your data in a machine-readable format.
          </li>
          <li>
            <strong>Right to object:</strong> You can object to processing based on legitimate interests, including direct marketing.
          </li>
        </ul>
        <p>
          To exercise any of these rights, please contact us at{" "}
          <a href={`mailto:${siteConfig.contact.email}`} className="text-[var(--accent-strong)] underline">
            {siteConfig.contact.email}
          </a>
          . We will respond within one month.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">7. Cookies</h2>
        <p>
          We use cookies for analytics purposes. For full details on what cookies we use and how to manage them, please see our{" "}
          <a href="/cookie-policy" className="text-[var(--accent-strong)] underline">
            cookie policy
          </a>
          .
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">8. International transfers</h2>
        <p>
          Some of our third-party service providers (e.g., Vercel) are based outside the UK and EEA. Where data is transferred internationally, we ensure appropriate safeguards are in place, such as EU-US Data Privacy Framework certification or Standard Contractual Clauses.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">9. Changes to this policy</h2>
        <p>
          We may update this privacy policy from time to time. The &quot;Last updated&quot; date at the top of this page shows when it was last revised. We encourage you to review this policy periodically.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">10. Complaints</h2>
        <p>
          If you believe we have not handled your personal data properly, you have the right to lodge a complaint with the Information Commissioner&apos;s Office (ICO), the UK&apos;s data protection regulator. You can contact the ICO at{" "}
          <a
            href="https://ico.org.uk/make-a-complaint/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--accent-strong)] underline"
          >
            ico.org.uk/make-a-complaint
          </a>
          .
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">11. Contact us</h2>
        <p>
          If you have any questions about this privacy policy or how we handle your data, please contact us:
        </p>
        <ul className="list-none space-y-1 pl-0">
          <li>
            Email:{" "}
            <a href={`mailto:${siteConfig.contact.email}`} className="text-[var(--accent-strong)] underline">
              {siteConfig.contact.email}
            </a>
          </li>
          <li>
            Phone:{" "}
            <a href={`tel:${siteConfig.contact.phone.replace(/\s/g, "")}`} className="text-[var(--accent-strong)] underline">
              {siteConfig.contact.phone}
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}
