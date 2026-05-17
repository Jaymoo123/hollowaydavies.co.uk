import type { Metadata } from "next";
import Link from "next/link";
import { btnPrimary, btnSecondary, siteContainerLg, sectionY } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: `Thank you`,
  description: "Your enquiry has been received.",
  robots: { index: false, follow: true },
};

export default function ThankYouPage() {
  return (
    <section className={`${sectionY} bg-[#fafaf7]`}>
      <div className={siteContainerLg}>
        <div className="max-w-2xl">
          <p className="font-mono text-xs uppercase tracking-widest text-orange-500">
            Received
          </p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl lg:text-6xl">
            Thank you.
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-neutral-600">
            Your message is with an accountant on the team. We aim to reply within one
            working day, usually the same day.
          </p>
          <p className="mt-4 text-base leading-relaxed text-neutral-600">
            Urgent? Call us directly on{" "}
            <a
              href={`tel:${siteConfig.contact.phone.replace(/\s/g, "")}`}
              className="font-medium text-neutral-900 underline underline-offset-4 hover:text-orange-600"
            >
              {siteConfig.contact.phone}
            </a>
            .
          </p>
          <div className="mt-12 flex flex-col gap-3 sm:flex-row">
            <Link href="/" className={btnPrimary}>
              Back to home
            </Link>
            <Link href="/calculators" className={btnSecondary}>
              Try the free calculators
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
