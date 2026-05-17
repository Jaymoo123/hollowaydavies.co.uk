import Link from "next/link";
import { focusRing, siteContainerLg } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";
import { SignupForm } from "@/components/newsletter/SignupForm";

export function SiteFooter() {
  const year = new Date().getFullYear();

  // Split footer links into rough three-column groups for visual rhythm.
  const links = siteConfig.footer;
  const colSize = Math.ceil(links.length / 3);
  const col1 = links.slice(0, colSize);
  const col2 = links.slice(colSize, colSize * 2);
  const col3 = links.slice(colSize * 2);

  return (
    <footer className="border-t border-neutral-200 bg-[#fafaf7]">
      <div className={`${siteContainerLg} pt-16 pb-10 sm:pt-20 sm:pb-12`}>
        <div className="grid gap-12 md:grid-cols-[1.4fr_1fr_1fr_1fr] md:gap-10">
          {/* Brand + newsletter capture */}
          <div className="min-w-0">
            <div className="font-mono text-xs uppercase tracking-widest text-orange-500">
              {siteConfig.legalName}
            </div>
            <div className="mt-3 text-xl font-semibold tracking-tight text-neutral-900">
              {siteConfig.name}
            </div>
            <p className="mt-3 max-w-sm text-sm leading-relaxed text-neutral-600">
              {siteConfig.description}
            </p>
            <div className="mt-8 max-w-md">
              <SignupForm
                source="footer"
                variant="inline"
                heading="The Director's Brief"
                body="One short note a week. UK business tax, structure, payroll, cash."
                ctaLabel="Subscribe"
              />
            </div>
          </div>

          {/* Three link columns */}
          {[col1, col2, col3].map((col, i) => (
            <div key={i} className="min-w-0">
              <ul className="space-y-3">
                {col.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={`text-sm text-neutral-600 transition-colors hover:text-neutral-900 ${focusRing}`}
                    >
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-16 flex flex-col gap-2 border-t border-neutral-200 pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-neutral-500">
            &copy; {year} {siteConfig.legalName}. Registered in England and Wales.
          </p>
          <p className="text-xs text-neutral-500">
            ICAEW chartered accountants. Editorial content; book a call for advice specific to your business.
          </p>
        </div>
      </div>
    </footer>
  );
}
