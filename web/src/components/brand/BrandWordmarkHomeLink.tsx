import Image from "next/image";
import Link from "next/link";
import { focusRing } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";

type BrandWordmarkHomeLinkProps = {
  className?: string;
  size?: "header" | "footer";
};

export function BrandWordmarkHomeLink({ className = "", size = "header" }: BrandWordmarkHomeLinkProps) {
  const isFooter = size === "footer";
  // Primary logo is 1206x270 (4.47:1 aspect). Width-constrained, height auto.
  const widthClass = isFooter
    ? "w-[200px] sm:w-[220px]"
    : "w-[160px] sm:w-[200px]";

  return (
    <Link
      href="/"
      aria-label={`${siteConfig.name} - ${siteConfig.tagline}`}
      className={`group inline-flex items-center ${focusRing} rounded-lg ${className}`.trim()}
    >
      <Image
        src="/brand/primary-logo.png"
        alt={siteConfig.name}
        width={1206}
        height={270}
        priority={!isFooter}
        className={`${widthClass} h-auto`}
      />
    </Link>
  );
}
