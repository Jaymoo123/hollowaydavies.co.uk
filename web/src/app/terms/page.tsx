import type { Metadata } from "next";
import Link from "next/link";
import { contentNarrow, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { Breadcrumb } from "@/components/ui/Breadcrumb";

export const metadata: Metadata = {
  title: "Terms of use",
  description: `Terms of use for the ${siteConfig.name} website. Governing law, disclaimers, and acceptable use policy.`,
  alternates: { canonical: `${siteConfig.url}/terms` },
  openGraph: {
    title: `Terms of Use | ${siteConfig.name}`,
    description: `Terms of use for the ${siteConfig.name} website. Governing law, disclaimers, and acceptable use policy.`,
    url: `${siteConfig.url}/terms`,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Terms of use",
    description: `Terms of use for the ${siteConfig.name} website. Governing law, disclaimers, and acceptable use policy.`,
  },
};

export default function TermsPage() {
  return (
    <div className={`${contentNarrow} ${sectionY}`}>
      <Breadcrumb
        items={[
          { label: "Home", href: "/" },
          { label: "Terms of use" },
        ]}
      />
      <h1 className="font-serif text-3xl font-semibold text-[var(--ink)] sm:text-4xl">Terms of use</h1>
      <p className="mt-4 text-sm text-[var(--muted)]">Last updated: 27 March 2026</p>
      <div className="prose-blog mt-8 space-y-6 text-[var(--ink-soft)]">
        <p>
          These terms of use govern your access to and use of the {siteConfig.name} website (the &quot;Site&quot;). By accessing or using the Site, you agree to be bound by these terms. If you do not agree, please do not use the Site.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">1. About us</h2>
        <p>
          The Site is operated by {siteConfig.legalName}. You can contact us at{" "}
          <a href={`mailto:${siteConfig.contact.email}`} className="text-[var(--accent-strong)] underline">
            {siteConfig.contact.email}
          </a>{" "}
          or by using the details on our{" "}
          <Link href="/contact" className="text-[var(--accent-strong)] underline">
            contact page
          </Link>
          .
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">2. No advice provided on the Site</h2>
        <p>
          Content on this Site is for general information purposes only. It does <strong>not</strong> constitute accounting, tax, financial, or legal advice. You should not rely on any content on the Site as a substitute for professional advice tailored to your specific circumstances.
        </p>
        <p>
          Formal engagements for professional services are subject to separate written engagement letters and terms of business. No accountant-client relationship is created by your use of this Site or submission of an enquiry form.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">3. Accuracy and changes</h2>
        <p>
          While we aim to keep information on the Site accurate and up to date, tax and accounting rules change frequently. We make no representations or warranties regarding the accuracy, completeness, or currency of any content.
        </p>
        <p>
          We reserve the right to update, modify, or remove content at any time without notice. It is your responsibility to check for updates if you are relying on information from the Site.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">4. Acceptable use</h2>
        <p>You agree not to:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>Use the Site in any way that violates applicable laws or regulations</li>
          <li>Attempt to gain unauthorised access to any part of the Site, server, or database</li>
          <li>Use automated systems (bots, scrapers) to access the Site without our prior written consent</li>
          <li>Transmit any harmful code, viruses, or malicious software</li>
          <li>Interfere with or disrupt the Site or servers</li>
          <li>Impersonate any person or entity, or misrepresent your affiliation with any person or entity</li>
        </ul>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">5. Intellectual property</h2>
        <p>
          All content on the Site, including text, graphics, logos, and software, is the property of {siteConfig.legalName} or its licensors and is protected by UK and international copyright laws.
        </p>
        <p>
          You may view and print pages from the Site for your personal, non-commercial use, provided you do not modify any content and you retain all copyright and proprietary notices. Any other use requires our prior written permission.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">6. Third-party links</h2>
        <p>
          The Site may contain links to third-party websites. We do not control or endorse these websites and are not responsible for their content, privacy practices, or terms of use. You access third-party websites at your own risk.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">7. Limitation of liability</h2>
        <p>
          To the fullest extent permitted by law, {siteConfig.legalName} excludes all liability for any loss or damage arising from your use of the Site, including but not limited to:
        </p>
        <ul className="list-disc space-y-2 pl-6">
          <li>Direct, indirect, incidental, or consequential losses</li>
          <li>Loss of profits, revenue, data, or business opportunities</li>
          <li>Errors, omissions, or inaccuracies in content</li>
          <li>Unavailability or interruption of the Site</li>
        </ul>
        <p>
          Nothing in these terms excludes or limits our liability for death or personal injury caused by negligence, fraud, or any other liability that cannot be excluded by law.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">8. Disclaimer of warranties</h2>
        <p>
          The Site is provided on an &quot;as is&quot; and &quot;as available&quot; basis. We make no warranties, express or implied, regarding the Site&apos;s operation, content, or suitability for any purpose. This includes implied warranties of merchantability, fitness for a particular purpose, and non-infringement.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">9. Indemnity</h2>
        <p>
          You agree to indemnify and hold harmless {siteConfig.legalName}, its directors, employees, and agents from any claims, losses, damages, liabilities, and expenses (including legal fees) arising from your use of the Site or breach of these terms.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">10. Governing law and jurisdiction</h2>
        <p>
          These terms are governed by the laws of England and Wales. Any disputes arising from these terms or your use of the Site shall be subject to the exclusive jurisdiction of the courts of England and Wales.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">11. Changes to these terms</h2>
        <p>
          We may update these terms from time to time. The &quot;Last updated&quot; date at the top of this page shows when they were last revised. Your continued use of the Site after changes are posted constitutes your acceptance of the updated terms.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">12. Severability</h2>
        <p>
          If any provision of these terms is found to be invalid or unenforceable, the remaining provisions shall continue in full force and effect.
        </p>

        <h2 className="font-serif text-xl font-semibold text-[var(--ink)]">13. Contact us</h2>
        <p>
          Questions about these terms? Contact us at{" "}
          <a href={`mailto:${siteConfig.contact.email}`} className="text-[var(--accent-strong)] underline">
            {siteConfig.contact.email}
          </a>{" "}
          or via our{" "}
          <Link href="/contact" className="text-[var(--accent-strong)] underline">
            contact page
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
