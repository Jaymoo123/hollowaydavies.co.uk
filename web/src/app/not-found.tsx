import Link from "next/link";
import { btnPrimary, sectionY } from "@/components/ui/layout-utils";

export default function NotFound() {
  return (
    <div
      className={`mx-auto w-full max-w-lg min-w-0 px-4 sm:px-6 lg:px-8 ${sectionY} text-center`}
    >
      <h1 className="font-serif text-3xl font-semibold text-[var(--ink)] sm:text-4xl">Page not found</h1>
      <p className="mt-4 text-base leading-relaxed text-[var(--muted)]">
        The page you requested does not exist or has moved.
      </p>
      <p className="mt-8 flex justify-center">
        <Link href="/" className={`${btnPrimary} w-full max-w-xs sm:w-auto`}>
          Back to homepage
        </Link>
      </p>
    </div>
  );
}
