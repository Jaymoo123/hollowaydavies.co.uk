"use client";

import { useEffect } from "react";
import Link from "next/link";
import { btnPrimary, siteContainer } from "@/components/ui/layout-utils";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.error('Error boundary caught:', error);
    }
  }, [error]);

  return (
    <div className={`${siteContainer} py-16 sm:py-24`}>
      <div className="mx-auto max-w-2xl text-center">
        <div className="mb-8">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-slate-900 sm:text-4xl">
          Something went wrong
        </h1>
        
        <p className="mt-4 text-lg text-slate-600">
          We encountered an unexpected error. This has been logged and we&apos;ll look into it.
        </p>

        {process.env.NODE_ENV === 'development' && error.message && (
          <div className="mt-6 rounded-lg bg-red-50 border border-red-200 p-4 text-left">
            <p className="text-sm font-mono text-red-800 break-words">
              {error.message}
            </p>
          </div>
        )}

        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            onClick={reset}
            className={`${btnPrimary} inline-flex`}
          >
            Try again
          </button>
          <Link
            href="/"
            className="inline-flex items-center justify-center rounded-lg border-2 border-slate-300 bg-white px-6 py-3 text-base font-semibold text-slate-900 transition-colors hover:border-slate-400 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
          >
            Go home
          </Link>
        </div>

        <p className="mt-8 text-sm text-slate-500">
          If this keeps happening, please{" "}
          <a href="/contact" className="font-semibold text-orange-700 hover:text-orange-600">
            get in touch
          </a>
          .
        </p>
      </div>
    </div>
  );
}
