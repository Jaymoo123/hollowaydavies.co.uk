"use client";

import { useState, useEffect } from "react";
import { focusRing } from "@/components/ui/layout-utils";

type Heading = {
  id: string;
  text: string;
  level: number;
};

type TableOfContentsProps = {
  headings: Heading[];
};

export function TableOfContents({ headings }: TableOfContentsProps) {
  const [activeId, setActiveId] = useState<string>("");

  useEffect(() => {
    if (headings.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: "-100px 0px -66%" }
    );

    headings.forEach((h) => {
      const el = document.getElementById(h.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [headings]);

  if (headings.length === 0) return null;

  return (
    <nav aria-label="Table of contents">
      {/* Mobile: Sticky at top, compact */}
      <div className="lg:hidden sticky top-16 z-30 mb-6 -mx-4 sm:-mx-6">
        <div className="bg-[var(--surface)]/95 backdrop-blur-sm border-y border-[var(--border)] px-4 py-3 sm:px-6">
          <details className="group">
            <summary className={`flex items-center justify-between cursor-pointer list-none ${focusRing} rounded`}>
              <span className="flex items-center gap-2 text-sm font-semibold text-[var(--ink)]">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                On this page
              </span>
              <svg
                className="w-5 h-5 text-[var(--muted)] transition-transform group-open:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            <ul className="mt-3 space-y-1 max-h-[60vh] overflow-y-auto">
              {headings.map((h) => (
                <li key={h.id} style={{ paddingLeft: `${(h.level - 2) * 1}rem` }}>
                  <a
                    href={`#${h.id}`}
                    className={`block min-h-[44px] flex items-center px-3 py-2 text-sm rounded transition-colors ${focusRing} ${
                      activeId === h.id
                        ? "text-[var(--primary)] font-semibold bg-[var(--primary)]/5 border-l-2 border-[var(--primary)]"
                        : "text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--primary)]/5"
                    }`}
                  >
                    {h.text}
                  </a>
                </li>
              ))}
            </ul>
          </details>
        </div>
      </div>

      {/* Desktop: Sticky sidebar */}
      <div className="hidden lg:block sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm">
        <h2 className="text-sm font-bold uppercase tracking-wide text-[var(--ink)] mb-4 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          On this page
        </h2>
        <ul className="space-y-1">
          {headings.map((h) => (
            <li key={h.id} style={{ paddingLeft: `${(h.level - 2) * 0.75}rem` }}>
              <a
                href={`#${h.id}`}
                className={`block px-3 py-2 text-sm rounded transition-colors ${focusRing} ${
                  activeId === h.id
                    ? "text-[var(--primary)] font-semibold bg-[var(--primary)]/5 border-l-2 border-[var(--primary)]"
                    : "text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--primary)]/5"
                }`}
              >
                {h.text}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
