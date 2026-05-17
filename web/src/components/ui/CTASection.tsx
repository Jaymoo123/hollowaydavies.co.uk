"use client";

import Link from "next/link";
import { useId } from "react";
import { btnPrimary, btnSecondary } from "@/components/ui/layout-utils";

type CTASectionProps = {
  title: string;
  description: string;
  primaryHref?: string;
  primaryLabel?: string;
  secondaryHref?: string;
  secondaryLabel?: string;
};

export function CTASection({
  title,
  description,
  primaryHref = "/contact",
  primaryLabel = "Speak to a specialist",
  secondaryHref = "/services",
  secondaryLabel = "View services",
}: CTASectionProps) {
  const headingId = useId();
  
  return (
    <section
      className="border-l-4 border-emerald-600 bg-emerald-50 p-8 sm:p-12"
      aria-labelledby={headingId}
    >
      <h2
        id={headingId}
        className="max-w-2xl text-2xl font-bold leading-tight text-slate-900 sm:text-3xl"
      >
        {title}
      </h2>
      <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-700">
        {description}
      </p>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
        <Link href={primaryHref} className={`${btnPrimary} w-full min-w-0 sm:w-auto`}>
          {primaryLabel}
        </Link>
        <Link href={secondaryHref} className={`${btnSecondary} w-full min-w-0 sm:w-auto`}>
          {secondaryLabel}
        </Link>
      </div>
    </section>
  );
}
