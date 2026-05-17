import Link from "next/link";
import { focusRing } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";

export function BrandLogoHero() {
  const [firstLine, secondLine] = siteConfig.name.split(" ").length > 2 
    ? [siteConfig.name.split(" ").slice(0, -1).join(" "), siteConfig.name.split(" ").slice(-1)[0]]
    : [siteConfig.name, ""];

  return (
    <div className="mb-6 sm:mb-8">
      <Link
        href="/"
        className={`group inline-flex max-w-full flex-col leading-none ${focusRing} rounded-lg outline-offset-4`}
      >
        <span className="text-2xl font-bold uppercase tracking-wider text-slate-900 sm:text-3xl md:text-4xl">
          {firstLine}
        </span>
        {secondLine && (
          <span className="mt-2 border-t-2 border-emerald-600 pt-2 text-lg font-bold uppercase tracking-wider text-slate-900 sm:mt-2.5 sm:pt-2.5 sm:text-xl md:text-2xl">
            {secondLine}
          </span>
        )}
        <span className="sr-only">, {siteConfig.tagline}</span>
      </Link>
    </div>
  );
}
