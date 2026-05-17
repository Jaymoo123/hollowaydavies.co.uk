"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useState } from "react";
import { BrandWordmarkHomeLink } from "@/components/brand/BrandWordmarkHomeLink";
import { btnPrimary, focusRing, siteContainerLg } from "@/components/ui/layout-utils";
import { siteConfig } from "@/config/site";

function MenuIcon({ open }: { open: boolean }) {
  return (
    <svg
      className="h-5 w-5 text-neutral-900"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.75}
      aria-hidden
    >
      {open ? (
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
      ) : (
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      )}
    </svg>
  );
}

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const panelId = useId();

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    const prev = document.documentElement.style.overflow;
    document.documentElement.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.documentElement.style.overflow = prev;
    };
  }, [open]);

  return (
    <header
      className="sticky top-0 z-40 border-b border-neutral-200 bg-[#fafaf7]/95 backdrop-blur supports-[backdrop-filter]:bg-[#fafaf7]/80"
      style={{
        paddingTop: "max(0px, env(safe-area-inset-top))",
      }}
    >
      <div
        className={`${siteContainerLg} flex min-h-14 items-center justify-between gap-3 py-3 sm:min-h-16 sm:gap-6`}
      >
        <BrandWordmarkHomeLink />

        <nav
          aria-label="Primary"
          className="hidden min-w-0 items-center gap-8 md:flex"
        >
          {siteConfig.nav.map((item) => {
            const children = item.children;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`) ||
              !!children?.some((c) => pathname === c.href || pathname.startsWith(`${c.href}/`));

            if (children && children.length > 0) {
              return (
                <div key={item.href} className="relative group">
                  <Link
                    href={item.href}
                    className={`inline-flex items-center gap-1 text-sm font-medium tracking-tight transition-colors ${focusRing} ${
                      active ? "text-neutral-900" : "text-neutral-600 hover:text-neutral-900"
                    }`}
                    aria-haspopup="true"
                  >
                    {item.label}
                    <svg className="h-3 w-3 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </Link>
                  <div className="invisible opacity-0 group-hover:visible group-hover:opacity-100 group-focus-within:visible group-focus-within:opacity-100 absolute left-0 top-full pt-2 transition-opacity">
                    <ul className="w-80 border border-neutral-200 bg-white py-2 shadow-lg" role="menu">
                      {children.map((child) => (
                        <li key={child.href} role="none">
                          <Link
                            href={child.href}
                            role="menuitem"
                            className={`block px-4 py-3 text-sm transition-colors hover:bg-neutral-50 ${focusRing}`}
                          >
                            <span className="font-medium text-neutral-900">{child.label}</span>
                            {child.description ? (
                              <span className="block mt-1 text-xs leading-relaxed text-neutral-500">{child.description}</span>
                            ) : null}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              );
            }

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`text-sm font-medium tracking-tight transition-colors ${focusRing} ${
                  active ? "text-neutral-900" : "text-neutral-600 hover:text-neutral-900"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/contact"
            className={`${btnPrimary} hidden min-h-10 px-5 py-2 text-xs sm:inline-flex`}
          >
            Book a free call
          </Link>

          <button
            type="button"
            className={`flex h-11 w-11 touch-manipulation items-center justify-center border border-neutral-300 bg-white text-neutral-900 hover:bg-neutral-50 md:hidden ${focusRing}`}
            aria-expanded={open}
            aria-controls={panelId}
            aria-label={open ? "Close menu" : "Open menu"}
            onClick={() => setOpen((v) => !v)}
          >
            <MenuIcon open={open} />
          </button>
        </div>
      </div>

      {open ? (
        <div
          className="fixed inset-0 z-50 md:hidden"
          role="dialog"
          aria-modal="true"
          aria-labelledby={`${panelId}-title`}
        >
          <button
            type="button"
            className="absolute inset-0 bg-neutral-900/50 backdrop-blur-[2px]"
            aria-label="Close menu"
            onClick={() => setOpen(false)}
          />
          <div
            id={panelId}
            className="absolute right-0 top-0 flex h-[100dvh] w-[min(22rem,92vw)] flex-col bg-white shadow-2xl"
            style={{
              paddingTop: "max(1rem, env(safe-area-inset-top))",
              paddingBottom: "max(1rem, env(safe-area-inset-bottom))",
            }}
          >
            <div className="flex flex-col gap-3 border-b border-neutral-200 px-5 py-4">
              <div className="flex items-center justify-between gap-2">
                <p id={`${panelId}-title`} className="font-mono text-xs uppercase tracking-widest text-orange-500">
                  Menu
                </p>
                <button
                  type="button"
                  className={`flex h-10 w-10 shrink-0 items-center justify-center border border-neutral-300 ${focusRing}`}
                  aria-label="Close menu"
                  onClick={() => setOpen(false)}
                >
                  <MenuIcon open />
                </button>
              </div>
              <BrandWordmarkHomeLink />
            </div>
            <nav aria-label="Mobile" className="flex flex-1 flex-col gap-0 overflow-y-auto px-5 py-4">
              {siteConfig.nav.map((item) => {
                const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                const children = item.children;
                return (
                  <div key={item.href} className="border-b border-neutral-200 py-1">
                    <Link
                      href={item.href}
                      className={`block py-3 text-base font-medium ${focusRing} ${
                        active ? "text-orange-600" : "text-neutral-900 hover:text-orange-600"
                      }`}
                      onClick={() => setOpen(false)}
                    >
                      {item.label}
                    </Link>
                    {children && children.length > 0 ? (
                      <ul className="mb-2 space-y-1">
                        {children.map((child) => (
                          <li key={child.href}>
                            <Link
                              href={child.href}
                              className={`block py-2 pl-4 text-sm text-neutral-600 hover:text-orange-600 ${focusRing}`}
                              onClick={() => setOpen(false)}
                            >
                              {child.label}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                );
              })}
            </nav>
            <div className="border-t border-neutral-200 px-5 py-4">
              <Link
                href="/contact"
                className={`${btnPrimary} w-full`}
                onClick={() => setOpen(false)}
              >
                Book a free call
              </Link>
            </div>
          </div>
        </div>
      ) : null}
    </header>
  );
}
